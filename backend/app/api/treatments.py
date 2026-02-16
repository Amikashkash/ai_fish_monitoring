"""
Filename: treatments.py
Purpose: Treatment protocol API endpoints
Author: Fish Monitoring System
Created: 2026-02-15

Handles treatment creation, updates, and retrieval.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.schemas.treatment import TreatmentCreate, TreatmentResponse
from app.crud import treatment as treatment_crud

router = APIRouter(prefix="/api/treatments", tags=["treatments"])


@router.post("/", response_model=TreatmentResponse, status_code=201)
async def create_treatment(
    treatment: TreatmentCreate,
    db: Session = Depends(get_db)
):
    """Create a new treatment protocol for a shipment."""
    try:
        db_treatment = treatment_crud.create_treatment(db=db, treatment=treatment)
        return db_treatment
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to create treatment")


@router.get("/{treatment_id}", response_model=TreatmentResponse)
async def get_treatment(
    treatment_id: int,
    db: Session = Depends(get_db)
):
    """Retrieve a treatment by ID."""
    treatment = treatment_crud.get_treatment(db, treatment_id)
    if not treatment:
        raise HTTPException(status_code=404, detail="Treatment not found")
    return treatment


@router.get("/", response_model=List[TreatmentResponse])
async def list_treatments(
    active_only: bool = False,
    db: Session = Depends(get_db)
):
    """List all treatments or only active ones."""
    if active_only:
        treatments = treatment_crud.get_active_treatments(db)
    else:
        treatments = treatment_crud.get_treatments(db)
    return treatments


@router.post("/{treatment_id}/complete", response_model=TreatmentResponse)
async def complete_treatment(
    treatment_id: int,
    db: Session = Depends(get_db)
):
    """Mark a treatment as completed."""
    treatment = treatment_crud.complete_treatment(db, treatment_id)
    if not treatment:
        raise HTTPException(status_code=404, detail="Treatment not found")
    return treatment
