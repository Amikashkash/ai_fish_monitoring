"""
Filename: supplier_scorer.py
Purpose: Score and rank fish suppliers based on historical performance
Author: Fish Monitoring System
Created: 2026-02-15

This module analyzes all supplier/source performance data to provide
reliability rankings and purchasing recommendations.
"""

from typing import List, Dict
from sqlalchemy.orm import Session

from app.ai.client import get_ai_client, get_default_model, get_default_max_tokens
from app.ai.prompts import SYSTEM_PROMPT_SUPPLIER, build_supplier_scoring_prompt
from app.crud import ai_knowledge
from app.schemas.recommendation import SupplierScore
from app.services.supplier_analyzer import analyze_supplier_performance


async def score_suppliers(db: Session) -> List[SupplierScore]:
    """
    Score and rank all suppliers based on historical performance.

    Analyzes success rates, sample sizes, and species-specific performance
    to provide comprehensive supplier reliability scores.

    Args:
        db: Database session

    Returns:
        List of SupplierScore objects, ranked by reliability

    Example:
        >>> scores = await score_suppliers(db)
        >>> for score in scores:
        ...     print(f"{score.source_country}: {score.overall_score}/100")
    """
    # Get all knowledge entries
    all_knowledge = ai_knowledge.get_all_knowledge(db)

    if not all_knowledge:
        return []

    # Group by supplier
    supplier_data = {}
    for k in all_knowledge:
        if k.source_country not in supplier_data:
            supplier_data[k.source_country] = []
        supplier_data[k.source_country].append(k)

    # Build prompt data
    prompt_data_lines = ["Supplier Performance Summary:"]
    for supplier, knowledge_list in supplier_data.items():
        total_shipments = sum(k.sample_size for k in knowledge_list)
        avg_success = sum(k.success_rate * k.sample_size for k in knowledge_list) / total_shipments if total_shipments > 0 else 0
        
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
        total_shipments = sum(k.sample_size for k in knowledge_list)
        avg_success = sum(k.success_rate * k.sample_size for k in knowledge_list) / total_shipments if total_shipments > 0 else 0
        
        # Simple scoring algorithm
        overall_score = min(100, int(avg_success))
        
        # Best performing species
        best_species = sorted(knowledge_list, key=lambda k: k.success_rate, reverse=True)[:3]
        best_species_list = [k.scientific_name for k in best_species]

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


def score_suppliers_sync(db: Session) -> List[SupplierScore]:
    """
    Synchronous version of score_suppliers.

    Args:
        db: Database session

    Returns:
        List of supplier scores

    Example:
        >>> scores = score_suppliers_sync(db)
    """
    import asyncio
    return asyncio.run(score_suppliers(db))
