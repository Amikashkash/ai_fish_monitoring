"""Follow-up assessment API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.schemas.followup import FollowupCreate, FollowupResponse
from app.crud import followup as followup_crud

router = APIRouter(prefix="/api/followups", tags=["followups"])


@router.post("/", response_model=FollowupResponse, status_code=201)
async def create_followup(
    followup: FollowupCreate,
    db: Session = Depends(get_db)
):
    """Create a 5-day follow-up assessment."""
    try:
        db_followup = followup_crud.create_followup(db=db, followup=followup)
        return db_followup
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to create follow-up")


@router.get("/treatment/{treatment_id}", response_model=FollowupResponse)
async def get_treatment_followup(
    treatment_id: int,
    db: Session = Depends(get_db)
):
    """Get follow-up assessment for a treatment."""
    followup = followup_crud.get_followup_by_treatment(db, treatment_id)
    if not followup:
        raise HTTPException(status_code=404, detail="Follow-up not found")
    return followup
