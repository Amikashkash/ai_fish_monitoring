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

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from supabase import Client

from app.ai.client import get_ai_client, get_default_model, get_default_max_tokens
from app.ai.prompt_builder import build_shipment_summary, build_historical_context
from app.ai.prompts import SYSTEM_PROMPT_PROTOCOL, build_protocol_prompt
from app.ai.protocol_template_service import build_protocol_template_context
from app.crud import shipment as shipment_crud
from app.crud import ai_knowledge
from app.schemas.recommendation import InitialProtocolRecommendation


async def recommend_initial_protocol(
    shipment_id: int,
    db: Session,
    supabase: Optional[Client] = None
) -> InitialProtocolRecommendation:
    """
    Recommend treatment protocol for a new fish shipment.

    Analyzes shipment details and historical data to suggest
    optimal drug protocols, dosages, and treatment duration.

    Args:
        shipment_id: ID of the new shipment
        db: Database session

    Returns:
        InitialProtocolRecommendation with:
        - confidence: Recommendation confidence level
        - recommended_drugs: List of drug protocols
        - expected_success_rate: Based on historical data
        - sample_size: Number of historical cases used
        - risk_factors: Key things to monitor
        - advice: Detailed AI recommendation text

    Raises:
        ValueError: If shipment not found

    Example:
        >>> recommendation = await recommend_initial_protocol(
        ...     shipment_id=1,
        ...     db=db
        ... )
        >>> for drug in recommendation.recommended_drugs:
        ...     print(f"{drug['name']}: {drug['dosage']}")
    """

    # Step 1: Get shipment details
    shipment = shipment_crud.get_shipment(db, shipment_id)
    if not shipment:
        raise ValueError(f"Shipment {shipment_id} not found")

    # Step 2: Get historical knowledge for this fish/source
    knowledge = ai_knowledge.get_knowledge_for_fish_source(
        db=db,
        scientific_name=shipment.scientific_name,
        source_country=shipment.source
    )

    # Step 3: Handle no historical data case
    if not knowledge or knowledge.sample_size == 0:
        return InitialProtocolRecommendation(
            confidence="no_data",
            recommended_drugs=[],
            expected_success_rate=None,
            sample_size=0,
            risk_factors=[
                "No historical data available",
                "First shipment of this species from this source",
                f"High density: {shipment.density} fish/L" if shipment.density > 0.2 else None
            ],
            advice=(
                f"No historical data for {shipment.scientific_name} "
                f"from {shipment.source}. Recommend starting with standard "
                "quarantine protocol: Methylene Blue 2-3 mg/L for 5 days. "
                "Monitor closely and adjust based on observations."
            )
        )

    # Step 4: Build AI prompt with protocol templates
    shipment_summary = build_shipment_summary(shipment)
    historical_context = build_historical_context(knowledge)

    # Add protocol template context if available
    protocol_template_context = ""
    if supabase:
        try:
            # Determine treatment purpose from shipment conditions
            # For now, we'll include general templates. In future, we can infer purpose from shipment.
            protocol_template_context = build_protocol_template_context(
                supabase=supabase,
                purpose=None,  # Get all proven templates
                limit=3
            )
        except Exception as e:
            print(f"Warning: Could not fetch protocol templates: {e}")
            protocol_template_context = ""

    user_prompt = build_protocol_prompt(
        shipment_summary=shipment_summary,
        historical_context=historical_context
    )

    # Append protocol template context to prompt
    if protocol_template_context:
        user_prompt += f"\n\n{protocol_template_context}\n\n" + \
                       "Consider the above protocol templates when making your recommendation. " + \
                       "If a template matches the situation well and has proven success, recommend it."

    # Step 5: Call Claude API
    client = get_ai_client()

    try:
        response = client.messages.create(
            model=get_default_model(),
            max_tokens=get_default_max_tokens(),
            system=SYSTEM_PROMPT_PROTOCOL,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )

        ai_text = response.content[0].text

        # Step 6: Parse and return recommendation
        return _parse_protocol_response(
            ai_text=ai_text,
            knowledge=knowledge,
            shipment=shipment
        )

    except Exception as e:
        # Fallback if AI fails
        return InitialProtocolRecommendation(
            confidence="medium",
            recommended_drugs=_extract_drugs_from_knowledge(knowledge),
            expected_success_rate=knowledge.success_rate,
            sample_size=knowledge.sample_size,
            risk_factors=[f"Density: {shipment.density} fish/L"],
            advice=(
                f"Based on {knowledge.sample_size} historical shipments, "
                f"success rate is {knowledge.success_rate}%. "
                f"AI analysis temporarily unavailable: {str(e)}"
            )
        )


def _parse_protocol_response(
    ai_text: str,
    knowledge,
    shipment
) -> InitialProtocolRecommendation:
    """
    Parse AI protocol recommendation into structured format.

    Args:
        ai_text: AI response text
        knowledge: Historical knowledge record
        shipment: Current shipment record

    Returns:
        Structured recommendation object
    """
    confidence = "medium"
    ai_lower = ai_text.lower()

    if "high confidence" in ai_lower:
        confidence = "high"
    elif "low confidence" in ai_lower or "limited" in ai_lower:
        confidence = "low"

    # Extract drugs from knowledge base as fallback
    recommended_drugs = _extract_drugs_from_knowledge(knowledge)

    # Identify risk factors
    risk_factors = []
    if shipment.density > 0.2:
        risk_factors.append(f"High density: {shipment.density} fish/L")
    if knowledge.success_rate and knowledge.success_rate < 80:
        risk_factors.append(f"Historical success rate below 80%")

    return InitialProtocolRecommendation(
        confidence=confidence,
        recommended_drugs=recommended_drugs,
        expected_success_rate=knowledge.success_rate,
        sample_size=knowledge.sample_size,
        risk_factors=risk_factors,
        advice=ai_text
    )


def _extract_drugs_from_knowledge(knowledge) -> List[Dict[str, Any]]:
    """
    Extract drug list from knowledge base protocols.

    Args:
        knowledge: AI knowledge record

    Returns:
        List of drug dictionaries
    """
    if not knowledge or not knowledge.successful_protocols:
        return []

    drugs = []
    protocols = knowledge.successful_protocols

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


def recommend_initial_protocol_sync(
    shipment_id: int,
    db: Session,
    supabase: Optional[Client] = None
) -> InitialProtocolRecommendation:
    """
    Synchronous version of recommend_initial_protocol.

    Use in non-async contexts.

    Args:
        shipment_id: Shipment ID
        db: Database session
        supabase: Optional Supabase client for protocol templates

    Returns:
        Protocol recommendation

    Example:
        >>> recommendation = recommend_initial_protocol_sync(
        ...     shipment_id=1,
        ...     db=db,
        ...     supabase=supabase
        ... )
    """
    import asyncio
    return asyncio.run(recommend_initial_protocol(shipment_id, db, supabase))
