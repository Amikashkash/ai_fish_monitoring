"""
Filename: protocol_recommender.py
Purpose: Recommend initial treatment protocols for new fish shipments
Author: Fish Monitoring System
Created: 2026-02-15

This module provides AI-powered protocol recommendations based on
historical treatment success for similar fish species from the same source.

Dependencies:
    - app.ai.client: Claude API client
    - app.ai.prompt_builder: Context builders
    - app.crud: Database operations
    - anthropic: Claude SDK

Example:
    >>> from app.ai.protocol_recommender import recommend_initial_protocol
    >>> protocol = await recommend_initial_protocol(shipment_id=1, db=db)
    >>> print(protocol.confidence)  # "high" | "medium" | "low" | "no_data"
"""

from typing import List, Dict, Any
from supabase import Client

from app.ai.client import get_ai_client, get_default_model, get_default_max_tokens
from app.ai.prompts import SYSTEM_PROMPT_PROTOCOL, build_protocol_prompt
from app.ai.protocol_template_service import build_protocol_template_context
from app.schemas.recommendation import InitialProtocolRecommendation


def _build_shipment_summary(shipment: dict) -> str:
    """Format shipment dict into summary string for AI prompt."""
    density = shipment.get("density")
    density_str = f"{density} fish/L" if density is not None else "N/A"
    return (
        f"Shipment Details:\n"
        f"- Species: {shipment.get('scientific_name', '')} ({shipment.get('common_name', '')})\n"
        f"- Source: {shipment.get('source', '')}\n"
        f"- Quantity: {shipment.get('quantity', 0)} fish\n"
        f"- Volume: {shipment.get('aquarium_volume_liters', 0)}L\n"
        f"- Density: {density_str}\n"
        f"- Fish Size: {shipment.get('fish_size') or 'Not specified'}"
    )


def _build_historical_context(knowledge: dict) -> str:
    """Format ai_knowledge dict into context string for AI prompt."""
    lines = [
        f"Source: {knowledge.get('source_country', '')}",
        f"Species: {knowledge.get('scientific_name', '')}",
        f"Previous Shipments: {knowledge.get('sample_size', 0)}",
        f"Success Rate: {knowledge.get('success_rate', 0)}%",
    ]
    protocols = knowledge.get("successful_protocols")
    if protocols:
        lines.append("\nSuccessful Protocols:")
        if isinstance(protocols, dict):
            for key, value in protocols.items():
                lines.append(f"  - {key}: {value}")
        else:
            lines.append(f"  {protocols}")
    insights = knowledge.get("insights")
    if insights:
        lines.append("\nKey Insights:")
        lines.append(insights)
    return "\n".join(lines)


def _build_treatment_history(treatments: list) -> str:
    """Format past treatment records for this fish into a context string."""
    if not treatments:
        return ""
    lines = ["Past Treatments for This Fish:"]
    for i, t in enumerate(treatments, 1):
        drugs = t.get("treatment_drugs") or []
        drug_names = ", ".join(
            d.get("drug_name") or f"Protocol #{d.get('drug_protocol_id')}"
            for d in drugs
        ) or "Unknown drugs"
        outcome = t.get("outcome") or "unknown"
        score = t.get("outcome_score")
        score_str = f" ({score}/5 stars)" if score else ""
        mortality = t.get("total_mortality")
        mortality_str = f", {mortality} fish died" if mortality else ""
        notes = t.get("outcome_notes") or ""
        notes_str = f" — Notes: {notes}" if notes else ""
        lines.append(
            f"  Treatment {i}: {drug_names} -> Outcome: {outcome}{score_str}{mortality_str}{notes_str}"
        )
    return "\n".join(lines)


def recommend_initial_protocol(
    shipment_id: int,
    supabase: Client
) -> InitialProtocolRecommendation:
    """
    Recommend treatment protocol for a new fish shipment.

    Args:
        shipment_id: ID of the new shipment
        supabase: Supabase client

    Returns:
        InitialProtocolRecommendation with confidence, drugs, and advice

    Raises:
        ValueError: If shipment not found
    """
    # Step 1: Get shipment details from Supabase
    shipment_resp = supabase.table("shipments").select("*").eq("id", shipment_id).execute()
    if not shipment_resp.data:
        raise ValueError(f"Shipment {shipment_id} not found")
    shipment = shipment_resp.data[0]

    # Step 1b: Get past treatment history for this fish
    treatments_resp = (
        supabase.table("treatments")
        .select("*, treatment_drugs(*)")
        .eq("shipment_id", shipment_id)
        .order("created_at", desc=False)
        .execute()
    )
    past_treatments = treatments_resp.data or []

    # Step 2: Get historical knowledge for this fish/source
    knowledge_resp = (
        supabase.table("ai_knowledge")
        .select("*")
        .eq("scientific_name", shipment.get("scientific_name", ""))
        .eq("source_country", shipment.get("source", ""))
        .execute()
    )
    knowledge = knowledge_resp.data[0] if knowledge_resp.data else None

    # Step 3: Handle no historical data case
    if not knowledge or knowledge.get("sample_size", 0) == 0:
        density = shipment.get("density", 0) or 0
        return InitialProtocolRecommendation(
            confidence="no_data",
            recommended_drugs=[],
            expected_success_rate=None,
            sample_size=0,
            risk_factors=[
                "No historical data available",
                "First shipment of this species from this source",
                f"High density: {density} fish/L" if float(density) > 0.2 else None
            ],
            advice=(
                f"No historical data for {shipment.get('scientific_name', '')} "
                f"from {shipment.get('source', '')}. Recommend starting with standard "
                "quarantine protocol: Methylene Blue 2-3 mg/L for 5 days. "
                "Monitor closely and adjust based on observations."
            )
        )

    # Step 4: Build AI prompt
    shipment_summary = _build_shipment_summary(shipment)
    historical_context = _build_historical_context(knowledge)

    protocol_template_context = ""
    try:
        protocol_template_context = build_protocol_template_context(
            supabase=supabase,
            purpose=None,
            limit=3
        )
    except Exception as e:
        print(f"Warning: Could not fetch protocol templates: {e}")

    treatment_history = _build_treatment_history(past_treatments)
    user_prompt = build_protocol_prompt(
        shipment_summary=shipment_summary,
        historical_context=historical_context,
        treatment_history=treatment_history
    )

    if protocol_template_context:
        user_prompt += (
            f"\n\n{protocol_template_context}\n\n"
            "Consider the above protocol templates when making your recommendation. "
            "If a template matches the situation well and has proven success, recommend it."
        )

    # Step 5: Call Claude API
    client = get_ai_client()

    try:
        response = client.messages.create(
            model=get_default_model(),
            max_tokens=get_default_max_tokens(),
            system=SYSTEM_PROMPT_PROTOCOL,
            messages=[{"role": "user", "content": user_prompt}]
        )
        ai_text = response.content[0].text
        return _parse_protocol_response(ai_text=ai_text, knowledge=knowledge, shipment=shipment)

    except Exception as e:
        return InitialProtocolRecommendation(
            confidence="medium",
            recommended_drugs=_extract_drugs_from_knowledge(knowledge),
            expected_success_rate=knowledge.get("success_rate"),
            sample_size=knowledge.get("sample_size", 0),
            risk_factors=[f"Density: {shipment.get('density', 'N/A')} fish/L"],
            advice=(
                f"Based on {knowledge.get('sample_size', 0)} historical shipments, "
                f"success rate is {knowledge.get('success_rate', 0)}%. "
                f"AI analysis temporarily unavailable: {str(e)}"
            )
        )


def _parse_protocol_response(
    ai_text: str,
    knowledge: dict,
    shipment: dict
) -> InitialProtocolRecommendation:
    """Parse AI protocol recommendation into structured format."""
    confidence = "medium"
    ai_lower = ai_text.lower()

    if "high confidence" in ai_lower:
        confidence = "high"
    elif "low confidence" in ai_lower or "limited" in ai_lower:
        confidence = "low"

    recommended_drugs = _extract_drugs_from_knowledge(knowledge)

    risk_factors = []
    density = float(shipment.get("density", 0) or 0)
    if density > 0.2:
        risk_factors.append(f"High density: {density} fish/L")
    success_rate = knowledge.get("success_rate", 100)
    if success_rate and float(success_rate) < 80:
        risk_factors.append("Historical success rate below 80%")

    return InitialProtocolRecommendation(
        confidence=confidence,
        recommended_drugs=recommended_drugs,
        expected_success_rate=knowledge.get("success_rate"),
        sample_size=knowledge.get("sample_size", 0),
        risk_factors=risk_factors,
        advice=ai_text
    )


def _extract_drugs_from_knowledge(knowledge: dict) -> List[Dict[str, Any]]:
    """Extract drug list from knowledge base protocols."""
    if not knowledge:
        return []

    protocols = knowledge.get("successful_protocols")
    if not protocols:
        return []

    drugs = []
    if isinstance(protocols, dict):
        for drug_name, details in protocols.items():
            drugs.append({
                "name": drug_name,
                "dosage": details.get("dosage", "As per protocol"),
                "frequency": details.get("frequency", "Once daily"),
                "duration": details.get("duration", "5 days")
            })
    elif isinstance(protocols, list):
        drugs = protocols

    return drugs
