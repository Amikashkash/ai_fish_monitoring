"""AI recommendation API endpoints using Supabase REST API."""

from fastapi import APIRouter, Depends, HTTPException
from supabase import Client

from app.config.supabase_client import get_supabase
from app.schemas.recommendation import PreShipmentAdvice, InitialProtocolRecommendation
from app.ai.pre_shipment_advisor import get_pre_shipment_advice
from app.ai.protocol_recommender import recommend_initial_protocol

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


@router.get("/pre-shipment", response_model=PreShipmentAdvice)
async def get_pre_shipment_recommendation(
    scientific_name: str,
    source_country: str,
    supabase: Client = Depends(get_supabase)
):
    """
    Get AI advice before ordering fish from a supplier.

    Args:
        scientific_name: Latin name of fish species
        source_country: Source country name

    Returns:
        Pre-shipment advice with confidence level and recommendations
    """
    try:
        advice = get_pre_shipment_advice(
            scientific_name=scientific_name,
            source_country=source_country,
            supabase=supabase
        )
        return advice
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI recommendation failed: {str(e)}")


@router.get("/protocol/{shipment_id}", response_model=InitialProtocolRecommendation)
async def get_protocol_recommendation(
    shipment_id: int,
    supabase: Client = Depends(get_supabase)
):
    """
    Get AI-recommended treatment protocol for a new shipment.

    Now includes protocol template recommendations based on historical success rates.

    Args:
        shipment_id: ID of the shipment

    Returns:
        Protocol recommendation with drugs, dosages, and confidence level
    """
    try:
        recommendation = recommend_initial_protocol(
            shipment_id=shipment_id,
            supabase=supabase
        )
        return recommendation
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI recommendation failed: {str(e)}")
