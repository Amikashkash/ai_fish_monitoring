"""
Filename: pre_shipment_advisor.py
Purpose: Provide AI-powered advice before ordering fish from suppliers
Author: Fish Monitoring System
Created: 2026-02-15

This module analyzes historical data to advise on the success likelihood
of ordering a specific fish species from a particular supplier/source.

Dependencies:
    - app.ai.client: Claude API client
    - app.ai.prompt_builder: Historical context builder
    - app.crud.ai_knowledge: Knowledge base access
    - app.schemas.recommendation: Response schemas
    - anthropic: Claude SDK

Example:
    >>> from app.ai.pre_shipment_advisor import get_pre_shipment_advice
    >>> advice = await get_pre_shipment_advice(
    ...     scientific_name="Betta splendens",
    ...     source_country="Thailand",
    ...     db_session=db
    ... )
    >>> print(advice.confidence)  # "high" | "medium" | "low" | "no_data"
"""

from typing import Optional
from sqlalchemy.orm import Session

from app.ai.client import get_ai_client, get_default_model, get_default_max_tokens
from app.ai.prompt_builder import build_historical_context
from app.ai.prompts import (
    SYSTEM_PROMPT_PRE_SHIPMENT,
    build_pre_shipment_prompt
)
from app.crud import ai_knowledge
from app.schemas.recommendation import PreShipmentAdvice


async def get_pre_shipment_advice(
    scientific_name: str,
    source_country: str,
    db: Session
) -> PreShipmentAdvice:
    """
    Get AI recommendation before ordering fish from a specific source.

    This function:
    1. Queries historical data for this fish/source combination
    2. Builds context for AI prompt
    3. Calls Claude API with "historical data only" constraint
    4. Returns advice with confidence level

    Args:
        scientific_name: Latin name of fish species (e.g., "Betta splendens")
        source_country: Origin country (e.g., "Thailand", "Sri Lanka")
        db: Database session for querying historical data

    Returns:
        PreShipmentAdvice object containing:
        - confidence: "high" | "medium" | "low" | "no_data"
        - success_rate: Historical success percentage (or None)
        - sample_size: Number of previous shipments (or 0)
        - recommendation: Text advice from AI
        - suggested_protocol: Drug protocol if available

    Example:
        >>> advice = await get_pre_shipment_advice(
        ...     scientific_name="Betta splendens",
        ...     source_country="Thailand",
        ...     db_session=db
        ... )
        >>> if advice.confidence == "high":
        ...     print(f"Safe to order! {advice.success_rate}% success rate")
        >>> elif advice.confidence == "no_data":
        ...     print("No historical data - proceed with caution")
    """

    # Step 1: Retrieve historical knowledge
    knowledge = ai_knowledge.get_knowledge_for_fish_source(
        db=db,
        scientific_name=scientific_name,
        source_country=source_country
    )

    # Step 2: Handle case with no historical data
    if not knowledge or knowledge.sample_size == 0:
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
    historical_context = build_historical_context(knowledge)
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
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )

        ai_text = response.content[0].text

        # Step 5: Parse AI response and return advice
        return _parse_ai_response(
            ai_text=ai_text,
            knowledge=knowledge
        )

    except Exception as e:
        # Fallback if AI fails
        return PreShipmentAdvice(
            confidence="medium",
            success_rate=knowledge.success_rate,
            sample_size=knowledge.sample_size,
            recommendation=(
                f"Based on {knowledge.sample_size} previous shipments, "
                f"success rate is {knowledge.success_rate}%. "
                f"AI analysis temporarily unavailable: {str(e)}"
            ),
            suggested_protocol=knowledge.successful_protocols
        )


def _parse_ai_response(ai_text: str, knowledge) -> PreShipmentAdvice:
    """
    Parse AI text response into structured PreShipmentAdvice object.

    Args:
        ai_text: Raw text response from Claude
        knowledge: Knowledge base record for fallback data

    Returns:
        Structured PreShipmentAdvice object
    """
    # Determine confidence level from response text
    confidence = "medium"  # Default
    ai_lower = ai_text.lower()

    if "high confidence" in ai_lower or "highly confident" in ai_lower:
        confidence = "high"
    elif "low confidence" in ai_lower or "limited data" in ai_lower:
        confidence = "low"
    elif "no data" in ai_lower or "insufficient" in ai_lower:
        confidence = "no_data"

    return PreShipmentAdvice(
        confidence=confidence,
        success_rate=knowledge.success_rate,
        sample_size=knowledge.sample_size,
        recommendation=ai_text,
        suggested_protocol=knowledge.successful_protocols
    )


def get_pre_shipment_advice_sync(
    scientific_name: str,
    source_country: str,
    db: Session
) -> PreShipmentAdvice:
    """
    Synchronous version of get_pre_shipment_advice.

    Use this when calling from non-async context (e.g., FastAPI sync endpoints).

    Args:
        scientific_name: Latin name of fish species
        source_country: Origin country
        db: Database session

    Returns:
        PreShipmentAdvice object

    Example:
        >>> advice = get_pre_shipment_advice_sync(
        ...     scientific_name="Betta splendens",
        ...     source_country="Thailand",
        ...     db=db
        ... )
    """
    import asyncio
    return asyncio.run(get_pre_shipment_advice(scientific_name, source_country, db))
