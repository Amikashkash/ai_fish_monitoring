"""Daily observation API endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.schemas.observation import ObservationCreate, ObservationResponse
from app.crud import observation as observation_crud

router = APIRouter(prefix="/api/observations", tags=["observations"])


@router.post("/", response_model=ObservationResponse, status_code=201)
async def create_observation(
    observation: ObservationCreate,
    db: Session = Depends(get_db)
):
    """Record a daily observation for a treatment."""
    try:
        db_obs = observation_crud.create_observation(db=db, observation=observation)
        return db_obs
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to create observation")


@router.get("/treatment/{treatment_id}", response_model=List[ObservationResponse])
async def get_treatment_observations(
    treatment_id: int,
    db: Session = Depends(get_db)
):
    """Get all observations for a specific treatment."""
    observations = observation_crud.get_observations_by_treatment(db, treatment_id)
    return observations
