"""
Filename: outcome_learner.py
Purpose: Learn from treatment outcomes to improve future recommendations
Author: Fish Monitoring System
Created: 2026-02-15

This module analyzes completed treatments and follow-up assessments
to extract insights and update the AI knowledge base.
"""

from typing import List
from sqlalchemy.orm import Session

from app.ai.client import get_ai_client, get_default_model, get_default_max_tokens
from app.ai.prompt_builder import build_treatment_summary, build_historical_context
from app.ai.prompts import SYSTEM_PROMPT_LEARNING, build_learning_prompt
from app.crud import treatment as treatment_crud
from app.crud import followup as followup_crud
from app.crud import ai_knowledge
from app.schemas.recommendation import AIInsights


async def learn_from_treatment(treatment_id: int, db: Session) -> AIInsights:
    """
    Analyze completed treatment and extract learnings.

    Args:
        treatment_id: ID of completed treatment
        db: Database session

    Returns:
        AIInsights object with learnings and recommendations

    Example:
        >>> insights = await learn_from_treatment(treatment_id=1, db=db)
    """
    treatment = treatment_crud.get_treatment(db, treatment_id)
    if not treatment:
        raise ValueError(f"Treatment {treatment_id} not found")

    followup = followup_crud.get_followup_by_treatment(db, treatment_id)
    if not followup:
        raise ValueError(f"No follow-up assessment found for treatment {treatment_id}")

    shipment = treatment.shipment
    knowledge = ai_knowledge.get_knowledge_for_fish_source(
        db=db, scientific_name=shipment.scientific_name, source_country=shipment.source
    )

    treatment_summary = build_treatment_summary(treatment, include_observations=True)
    followup_data = f"""Follow-up Assessment:
- Stability: {followup.stability_score}/5
- Success Rate: {followup.success_rate}%"""
    historical_context = build_historical_context(knowledge) if knowledge else "No previous data"

    user_prompt = build_learning_prompt(treatment_summary, followup_data, historical_context)

    client = get_ai_client()
    try:
        response = client.messages.create(
            model=get_default_model(),
            max_tokens=get_default_max_tokens(),
            system=SYSTEM_PROMPT_LEARNING,
            messages=[{"role": "user", "content": user_prompt}]
        )
        ai_text = response.content[0].text
        return AIInsights(
            key_learnings=[ai_text],
            suggested_changes=[],
            success_factors=[],
            preventive_measures=[],
            raw_analysis=ai_text
        )
    except Exception as e:
        return AIInsights(
            key_learnings=[f"Treatment result: {followup.success_rate}%"],
            suggested_changes=[],
            success_factors=[],
            preventive_measures=[],
            raw_analysis=f"AI analysis failed: {str(e)}"
        )
