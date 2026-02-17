"""Supplier scoring API endpoints using Supabase REST API."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from supabase import Client

from app.config.supabase_client import get_supabase
from app.schemas.recommendation import SupplierScore
from app.ai.supplier_scorer import score_suppliers

router = APIRouter(prefix="/api/suppliers", tags=["suppliers"])


@router.get("/scores", response_model=List[SupplierScore])
async def get_supplier_scores(supabase: Client = Depends(get_supabase)):
    """
    Get reliability scores for all suppliers.

    Returns list of suppliers ranked by performance, with:
    - Overall reliability score (0-100)
    - Success rates
    - Best performing species
    - Risk levels

    Returns:
        List of supplier scores, sorted by reliability (best first)
    """
    try:
        scores = score_suppliers(supabase)
        return scores
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scoring failed: {str(e)}")
