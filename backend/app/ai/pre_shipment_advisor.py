"""
Filename: pre_shipment_advisor.py
Purpose: Provide AI-powered advice before ordering fish from suppliers
Author: Fish Monitoring System
Created: 2026-02-15

This module analyzes historical data to advise on the success likelihood
of ordering a specific fish species from a particular supplier/source.
"""

from supabase import Client

from app.ai.client import get_ai_client, get_default_model, get_default_max_tokens
from app.ai.prompts import (
    SYSTEM_PROMPT_PRE_SHIPMENT,
    build_pre_shipment_prompt
)
from app.schemas.recommendation import PreShipmentAdvice


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


def get_pre_shipment_advice(
    scientific_name: str,
    source_country: str,
    supabase: Client
) -> PreShipmentAdvice:
    """
    Get AI recommendation before ordering fish from a specific source.

    Args:
        scientific_name: Latin name of fish species (e.g., "Betta splendens")
        source_country: Origin country (e.g., "Thailand", "Sri Lanka")
        supabase: Supabase client for querying historical data

    Returns:
        PreShipmentAdvice object containing confidence, success_rate, recommendation
    """
    # Step 1: Retrieve historical knowledge from Supabase
    response = (
        supabase.table("ai_knowledge")
        .select("*")
        .eq("scientific_name", scientific_name)
        .eq("source_country", source_country)
        .execute()
    )
    knowledge = response.data[0] if response.data else None

    # Step 2: Handle case with no historical data
    if not knowledge or knowledge.get("sample_size", 0) == 0:
        return PreShipmentAdvice(
            confidence="no_data",
            success_rate=None,
            sample_size=0,
            recommendation=(
                f"No historical data found for {scientific_name} "
                f"from {source_country}. This will be the first shipment. "
                "Proceed with standard quarantine protocols and monitor closely."
            ),
            suggested_protocol=None
        )

    # Step 3: Build AI prompt with historical context
    historical_context = _build_historical_context(knowledge)
    user_prompt = build_pre_shipment_prompt(
        scientific_name=scientific_name,
        source_country=source_country,
        historical_context=historical_context
    )

    # Step 4: Call Claude API
    client = get_ai_client()

    try:
        response = client.messages.create(
            model=get_default_model(),
            max_tokens=get_default_max_tokens(),
            system=SYSTEM_PROMPT_PRE_SHIPMENT,
            messages=[{"role": "user", "content": user_prompt}]
        )
        ai_text = response.content[0].text
        return _parse_ai_response(ai_text=ai_text, knowledge=knowledge)

    except Exception as e:
        return PreShipmentAdvice(
            confidence="medium",
            success_rate=knowledge.get("success_rate"),
            sample_size=knowledge.get("sample_size", 0),
            recommendation=(
                f"Based on {knowledge.get('sample_size', 0)} previous shipments, "
                f"success rate is {knowledge.get('success_rate', 0)}%. "
                f"AI analysis temporarily unavailable: {str(e)}"
            ),
            suggested_protocol=knowledge.get("successful_protocols")
        )


def _parse_ai_response(ai_text: str, knowledge: dict) -> PreShipmentAdvice:
    """Parse AI text response into structured PreShipmentAdvice object."""
    confidence = "medium"
    ai_lower = ai_text.lower()

    if "high confidence" in ai_lower or "highly confident" in ai_lower:
        confidence = "high"
    elif "low confidence" in ai_lower or "limited data" in ai_lower:
        confidence = "low"
    elif "no data" in ai_lower or "insufficient" in ai_lower:
        confidence = "no_data"

    return PreShipmentAdvice(
        confidence=confidence,
        success_rate=knowledge.get("success_rate"),
        sample_size=knowledge.get("sample_size", 0),
        recommendation=ai_text,
        suggested_protocol=knowledge.get("successful_protocols")
    )
