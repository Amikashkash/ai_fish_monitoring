"""
Filename: prompts.py
Purpose: Reusable prompt templates for AI interactions
Author: Fish Monitoring System
Created: 2026-02-15

This module defines system and user prompt templates for consistent
AI behavior across all features. All prompts enforce the critical
constraint: use ONLY historical data, no external research.

Dependencies:
    - None (pure text templates)

Example:
    >>> from app.ai.prompts import SYSTEM_PROMPT_BASE
    >>> print(SYSTEM_PROMPT_BASE)
"""

# Base system prompt enforcing historical data constraint
SYSTEM_PROMPT_BASE = """You are an expert fish health advisor specializing in ornamental fish acclimation.

CRITICAL CONSTRAINT: Use ONLY the historical data provided in the user's message.
Do NOT use any external knowledge, internet research, or general fish keeping advice.
Base your recommendations SOLELY on the patterns in the provided historical data.

If there is insufficient historical data, clearly state this limitation and recommend
standard quarantine protocols as a cautious baseline approach."""


# Pre-shipment advice system prompt
SYSTEM_PROMPT_PRE_SHIPMENT = f"""{SYSTEM_PROMPT_BASE}

Your task is to advise whether to order fish from a specific supplier/source.

Analyze the historical data and provide:
1. Confidence level (high/medium/low/no_data)
2. Success rate if available
3. Key patterns observed
4. Recommended protocol if available
5. Specific advice about this order

Format your response clearly with these sections."""


# Protocol recommendation system prompt
SYSTEM_PROMPT_PROTOCOL = f"""{SYSTEM_PROMPT_BASE}

Your task is to recommend an initial treatment protocol for a new fish shipment.

Analyze the historical data for this fish species from this source and provide:
1. Recommended drug protocols with dosages
2. Treatment duration
3. Confidence level based on sample size
4. Key risk factors to monitor
5. Expected success rate

If past treatments for this specific fish are listed, take them into account:
- Do NOT recommend drugs that already failed for this fish
- If a previous treatment succeeded, mention whether regression might indicate
  a different cause (water quality, secondary infection, etc.)
- If all previous treatments failed, escalate to a different drug class

Format your response with clear sections and specific dosages."""


# Outcome learning system prompt
SYSTEM_PROMPT_LEARNING = f"""{SYSTEM_PROMPT_BASE}

Your task is to analyze a completed treatment outcome and extract learnings.

Based on the treatment details and follow-up results:
1. Identify what worked well
2. Identify what could be improved
3. Determine if treatment duration should change for future cases
4. Suggest preventive measures for similar shipments
5. Update success patterns for this fish/source combination

Provide structured insights that can be stored in the knowledge base."""


# Supplier scoring system prompt
SYSTEM_PROMPT_SUPPLIER = f"""{SYSTEM_PROMPT_BASE}

Your task is to score and rank fish suppliers based on historical performance.

Analyze all shipment outcomes and provide:
1. Overall reliability score for each supplier (0-100)
2. Best performing fish species per supplier
3. Risk factors per supplier
4. Purchasing recommendations

Rank suppliers from most to least reliable."""


# User prompt builder functions

def build_pre_shipment_prompt(
    scientific_name: str,
    source_country: str,
    historical_context: str
) -> str:
    """Build user prompt for pre-shipment advice."""
    return f"""I am considering ordering {scientific_name} from {source_country}.

Historical Data:
{historical_context}

Based ONLY on this historical data, should I proceed with this order?
What protocol should I use if I order?"""


def build_protocol_prompt(
    shipment_summary: str,
    historical_context: str,
    treatment_history: str = ""
) -> str:
    """Build user prompt for protocol recommendation."""
    base = f"""New shipment received:

{shipment_summary}

Historical Data for this species/source:
{historical_context}"""

    if treatment_history:
        base += f"""

{treatment_history}

IMPORTANT: This fish has already been treated. Avoid repeating protocols that failed.
If all previous attempts failed, escalate to a different drug class."""

    base += """

Based ONLY on this historical data, what treatment protocol should I use?
Provide specific drug names, dosages, and duration."""
    return base


def build_learning_prompt(
    treatment_summary: str,
    followup_data: str,
    historical_context: str
) -> str:
    """Build user prompt for outcome learning."""
    return f"""Treatment completed:

{treatment_summary}

Follow-up Results:
{followup_data}

Current Knowledge Base:
{historical_context}

What can we learn from this outcome? What should we adjust for future shipments?"""


def build_supplier_scoring_prompt(supplier_data: str) -> str:
    """Build user prompt for supplier scoring."""
    return f"""Supplier Performance Data:

{supplier_data}

Based ONLY on this data, rank these suppliers by reliability.
Which suppliers should I prioritize for future orders?"""
