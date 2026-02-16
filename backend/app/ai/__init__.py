"""AI integration for fish health recommendations.

This package provides AI-powered advisory features using Claude API.
All recommendations are based STRICTLY on historical data from the system.

Modules:
    - client: Claude API client initialization
    - prompt_builder: Utilities for building AI prompts from data
    - prompts: Reusable prompt templates
    - pre_shipment_advisor: Pre-purchase advice based on history
    - protocol_recommender: Treatment protocol recommendations
    - outcome_learner: Learn from treatment outcomes
    - supplier_scorer: Score suppliers by performance
"""

from app.ai.client import get_ai_client
from app.ai.prompt_builder import (
    build_historical_context,
    build_shipment_summary,
    build_treatment_summary
)

__all__ = [
    "get_ai_client",
    "build_historical_context",
    "build_shipment_summary",
    "build_treatment_summary",
]
