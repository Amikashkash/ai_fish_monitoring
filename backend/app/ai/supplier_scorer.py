"""
Filename: supplier_scorer.py
Purpose: Score and rank fish suppliers based on historical performance
Author: Fish Monitoring System
Created: 2026-02-15

This module analyzes all supplier/source performance data to provide
reliability rankings and purchasing recommendations.
"""

from typing import List
from supabase import Client

from app.ai.client import get_ai_client, get_default_model, get_default_max_tokens
from app.ai.prompts import SYSTEM_PROMPT_SUPPLIER, build_supplier_scoring_prompt
from app.schemas.recommendation import SupplierScore


def score_suppliers(supabase: Client) -> List[SupplierScore]:
    """
    Score and rank all suppliers based on historical performance.

    Analyzes success rates, sample sizes, and species-specific performance
    to provide comprehensive supplier reliability scores.

    Args:
        supabase: Supabase client

    Returns:
        List of SupplierScore objects, ranked by reliability

    Example:
        >>> scores = score_suppliers(supabase)
        >>> for score in scores:
        ...     print(f"{score.source_country}: {score.overall_score}/100")
    """
    # Get all knowledge entries from Supabase
    response = supabase.table("ai_knowledge").select("*").execute()
    all_knowledge = response.data if response.data else []

    if not all_knowledge:
        return []

    # Group by supplier
    supplier_data = {}
    for k in all_knowledge:
        country = k.get("source_country", "Unknown")
        if country not in supplier_data:
            supplier_data[country] = []
        supplier_data[country].append(k)

    # Build prompt data
    prompt_data_lines = ["Supplier Performance Summary:"]
    for supplier, knowledge_list in supplier_data.items():
        total_shipments = sum(k.get("sample_size", 0) for k in knowledge_list)
        avg_success = (
            sum(k.get("success_rate", 0) * k.get("sample_size", 0) for k in knowledge_list) / total_shipments
            if total_shipments > 0 else 0
        )

        prompt_data_lines.append(f"\n{supplier}:")
        prompt_data_lines.append(f"  Total Shipments: {total_shipments}")
        prompt_data_lines.append(f"  Average Success Rate: {avg_success:.1f}%")
        prompt_data_lines.append(f"  Species Tracked: {len(knowledge_list)}")

    prompt_data = "\n".join(prompt_data_lines)
    user_prompt = build_supplier_scoring_prompt(prompt_data)

    # Call AI
    client = get_ai_client()
    try:
        response = client.messages.create(
            model=get_default_model(),
            max_tokens=get_default_max_tokens(),
            system=SYSTEM_PROMPT_SUPPLIER,
            messages=[{"role": "user", "content": user_prompt}]
        )
        ai_text = response.content[0].text
    except Exception as e:
        ai_text = f"AI scoring failed: {str(e)}"

    # Build supplier scores
    scores = []
    for supplier, knowledge_list in supplier_data.items():
        total_shipments = sum(k.get("sample_size", 0) for k in knowledge_list)
        avg_success = (
            sum(k.get("success_rate", 0) * k.get("sample_size", 0) for k in knowledge_list) / total_shipments
            if total_shipments > 0 else 0
        )

        overall_score = min(100, int(avg_success))

        best_species = sorted(knowledge_list, key=lambda k: k.get("success_rate", 0), reverse=True)[:3]
        best_species_list = [k.get("scientific_name", "") for k in best_species]

        scores.append(SupplierScore(
            source_country=supplier,
            overall_score=overall_score,
            total_shipments=total_shipments,
            average_success_rate=round(avg_success, 1),
            best_performing_species=best_species_list,
            recommendation=ai_text,
            risk_level="low" if avg_success >= 85 else "medium" if avg_success >= 70 else "high"
        ))

    # Sort by score
    scores.sort(key=lambda s: s.overall_score, reverse=True)
    return scores
