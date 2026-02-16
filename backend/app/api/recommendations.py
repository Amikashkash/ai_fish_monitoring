"""AI recommendation API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.schemas.recommendation import PreShipmentAdvice, InitialProtocolRecommendation
from app.ai.pre_shipment_advisor import get_pre_shipment_advice_sync
from app.ai.protocol_recommender import recommend_initial_protocol_sync

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


@router.get("/pre-shipment", response_model=PreShipmentAdvice)
async def get_pre_shipment_recommendation(
    scientific_name: str,
    source_country: str,
    db: Session = Depends(get_db)
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
        advice = get_pre_shipment_advice_sync(
            scientific_name=scientific_name,
            source_country=source_country,
            db=db
        )
        return advice
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI recommendation failed: {str(e)}")


@router.get("/protocol/{shipment_id}", response_model=InitialProtocolRecommendation)
async def get_protocol_recommendation(
    shipment_id: int,
    db: Session = Depends(get_db)
):
    """
    Get AI-recommended treatment protocol for a new shipment.

    Args:
        shipment_id: ID of the shipment

    Returns:
        Protocol recommendation with drugs, dosages, and confidence level
    """
    try:
        recommendation = recommend_initial_protocol_sync(
            shipment_id=shipment_id,
            db=db
        )
        return recommendation
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI recommendation failed: {str(e)}")
