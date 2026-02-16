"""
Protocol template service for AI recommendations.

This module handles querying and recommending protocol templates
based on treatment purpose and historical success rates.
"""

from typing import List, Dict, Any, Optional
from supabase import Client


def get_protocol_templates_by_purpose(
    supabase: Client,
    purpose: str,
    min_success_rate: Optional[float] = None,
    limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Get protocol templates for a specific treatment purpose.

    Args:
        supabase: Supabase client
        purpose: Treatment purpose (e.g., "bacterial infections")
        min_success_rate: Minimum success rate percentage filter
        limit: Maximum number of templates to return

    Returns:
        List of protocol template dictionaries with drug details
    """
    try:
        query = supabase.table("protocol_template_details").select("*").ilike("purpose", f"%{purpose}%")

        if min_success_rate is not None:
            query = query.gte("success_rate", min_success_rate)

        response = query.order("success_rate", desc=True).limit(limit).execute()

        return response.data if response.data else []
    except Exception as e:
        print(f"Error fetching protocol templates: {e}")
        return []


def get_all_protocol_templates_with_usage(
    supabase: Client,
    min_times_used: int = 1
) -> List[Dict[str, Any]]:
    """
    Get all protocol templates that have been used at least once.

    Args:
        supabase: Supabase client
        min_times_used: Minimum number of times template must have been used

    Returns:
        List of protocol template dictionaries with usage statistics
    """
    try:
        response = supabase.table("protocol_template_details").select("*").gte("times_used", min_times_used).order("success_rate", desc=True).execute()

        return response.data if response.data else []
    except Exception as e:
        print(f"Error fetching protocol templates: {e}")
        return []


def format_protocol_templates_for_prompt(templates: List[Dict[str, Any]]) -> str:
    """
    Format protocol templates into a text summary for AI prompt.

    Args:
        templates: List of protocol template dictionaries

    Returns:
        Formatted text string for inclusion in AI prompt
    """
    if not templates:
        return "No protocol templates available in the system yet."

    prompt_lines = ["Available Protocol Templates:"]

    for template in templates:
        template_name = template.get("template_name", "Unknown")
        purpose = template.get("purpose", "Unknown")
        duration = template.get("duration_days", "N/A")
        times_used = template.get("times_used", 0)
        success_rate = template.get("success_rate", 0)
        special_instructions = template.get("special_instructions")

        prompt_lines.append(f"\n**{template_name}**")
        prompt_lines.append(f"  - Purpose: {purpose}")
        prompt_lines.append(f"  - Duration: {duration} days")
        prompt_lines.append(f"  - Usage History: Used {times_used} times with {success_rate}% success rate")

        # Format drugs
        drugs = template.get("drugs", [])
        if drugs:
            prompt_lines.append("  - Drugs:")
            for drug in drugs:
                drug_name = drug.get("drug_name", "Unknown")
                dosage = drug.get("dosage", "N/A")
                frequency = drug.get("frequency", "N/A")
                prompt_lines.append(f"    • {drug_name}: {dosage}, {frequency}")

        if special_instructions:
            prompt_lines.append(f"  - Special Instructions: {special_instructions}")

    return "\n".join(prompt_lines)


def recommend_protocol_template(
    supabase: Client,
    purpose: str,
    prefer_proven: bool = True
) -> Optional[Dict[str, Any]]:
    """
    Recommend a single best protocol template for a given purpose.

    Args:
        supabase: Supabase client
        purpose: Treatment purpose
        prefer_proven: If True, only recommend templates that have been used before

    Returns:
        Best matching protocol template or None
    """
    min_usage = 1 if prefer_proven else 0
    min_success = 70.0 if prefer_proven else None

    templates = get_protocol_templates_by_purpose(
        supabase=supabase,
        purpose=purpose,
        min_success_rate=min_success,
        limit=1
    )

    if not templates:
        # Try again without success rate filter
        templates = get_protocol_templates_by_purpose(
            supabase=supabase,
            purpose=purpose,
            min_success_rate=None,
            limit=1
        )

    return templates[0] if templates else None


def build_protocol_template_context(
    supabase: Client,
    purpose: Optional[str] = None,
    limit: int = 5
) -> str:
    """
    Build context about protocol templates for AI prompt.

    Args:
        supabase: Supabase client
        purpose: Optional specific treatment purpose to filter by
        limit: Maximum templates to include

    Returns:
        Formatted context string for AI prompt
    """
    if purpose:
        templates = get_protocol_templates_by_purpose(
            supabase=supabase,
            purpose=purpose,
            limit=limit
        )
    else:
        templates = get_all_protocol_templates_with_usage(
            supabase=supabase,
            min_times_used=1
        )[:limit]

    return format_protocol_templates_for_prompt(templates)
