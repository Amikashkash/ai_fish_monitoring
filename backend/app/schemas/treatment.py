"""
Filename: treatment.py
Purpose: Pydantic schemas for treatment and treatment drug validation
Author: Fish Monitoring System
Created: 2026-02-15

This module defines schemas for treatment protocols and drug usage.

Dependencies:
    - pydantic: Data validation
    - datetime: Date handling

Example:
    >>> from app.schemas.treatment import TreatmentCreate
    >>> treatment = TreatmentCreate(
    ...     shipment_id=1,
    ...     start_date=Date.today(),
    ...     drugs=[{"drug_protocol_id": 1, "actual_dosage": 2.5}]
    ... )
"""

from pydantic import BaseModel, Field
from datetime import date as Date
from typing import Optional, List
from decimal import Decimal


class TreatmentDrugBase(BaseModel):
    """Base schema for treatment drug information."""

    drug_protocol_id: int = Field(..., gt=0)
    actual_dosage: Optional[Decimal] = Field(None, ge=0)
    actual_frequency: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None


class TreatmentDrugCreate(TreatmentDrugBase):
    """
    Schema for adding a drug to a treatment.

    Example:
        >>> drug = TreatmentDrugCreate(
        ...     drug_protocol_id=1,
        ...     actual_dosage=2.5,
        ...     actual_frequency="once daily"
        ... )
    """
    pass


class TreatmentDrugResponse(TreatmentDrugBase):
    """
    Schema for treatment drug in responses.

    Includes drug name from protocol.

    Example:
        >>> {
        ...     "id": 1,
        ...     "drug_name": "Methylene Blue",
        ...     "actual_dosage": 2.5,
        ...     "actual_frequency": "once daily"
        ... }
    """

    id: int
    drug_name: Optional[str] = None  # Populated from drug_protocol

    class Config:
        """Pydantic config for ORM mode."""
        from_attributes = True


class TreatmentBase(BaseModel):
    """Base treatment schema."""

    shipment_id: int = Field(..., gt=0)
    start_date: Date = Field(default_factory=Date.today)
    end_date: Optional[Date] = None
    status: str = Field(default="active", pattern="^(active|completed|modified)$")


class TreatmentCreate(TreatmentBase):
    """
    Schema for creating a new treatment.

    Includes list of drugs to use.

    Example:
        >>> treatment = TreatmentCreate(
        ...     shipment_id=1,
        ...     start_date=Date.today(),
        ...     drugs=[
        ...         {"drug_protocol_id": 1, "actual_dosage": 2.5},
        ...         {"drug_protocol_id": 2, "actual_dosage": 1.0}
        ...     ]
        ... )
    """

    drugs: List[TreatmentDrugCreate] = Field(default_factory=list)


class TreatmentUpdate(BaseModel):
    """
    Schema for updating a treatment.

    All fields optional for partial updates.

    Example:
        >>> update = TreatmentUpdate(
        ...     end_date=Date.today(),
        ...     status="completed"
        ... )
    """

    start_date: Optional[Date] = None
    end_date: Optional[Date] = None
    status: Optional[str] = Field(None, pattern="^(active|completed|modified)$")
    # Outcome fields — captured at graduation
    outcome: Optional[str] = Field(None, description="healthy | minor_loss | major_loss | total_loss")
    outcome_score: Optional[int] = Field(None, ge=1, le=5, description="1=very poor to 5=excellent")
    total_mortality: Optional[int] = Field(None, ge=0, description="Total fish found dead during treatment")
    outcome_notes: Optional[str] = None


class TreatmentResponse(TreatmentBase):
    """
    Schema for treatment in API responses.

    Example:
        >>> {
        ...     "id": 1,
        ...     "shipment_id": 1,
        ...     "start_date": "2026-02-15",
        ...     "status": "active",
        ...     "drugs": [...]
        ... }
    """

    id: int
    created_at: Optional[str] = None
    drugs: List[TreatmentDrugResponse] = Field(default_factory=list)
    # Outcome fields (populated after graduation)
    outcome: Optional[str] = None
    outcome_score: Optional[int] = None
    total_mortality: Optional[int] = None
    outcome_notes: Optional[str] = None

    class Config:
        """Pydantic config for ORM mode."""
        from_attributes = True


class TreatmentWithDetails(TreatmentResponse):
    """
    Extended treatment response with shipment and observation details.

    Example:
        >>> {
        ...     "id": 1,
        ...     "shipment_id": 1,
        ...     "fish_species": "Betta splendens",
        ...     "observation_count": 5,
        ...     "days_active": 7
        ... }
    """

    fish_species: Optional[str] = None
    fish_common_name: Optional[str] = None
    source: Optional[str] = None
    quantity: Optional[int] = None
    observation_count: int = 0
    days_active: int = 0


class TreatmentList(BaseModel):
    """
    Schema for paginated list of treatments.

    Example:
        >>> {
        ...     "total": 30,
        ...     "active_count": 5,
        ...     "treatments": [...]
        ... }
    """

    total: int
    active_count: int = 0
    page: int = 1
    page_size: int = 20
    treatments: List[TreatmentResponse]
