"""
Filename: observation.py
Purpose: Pydantic schemas for daily observation validation
Author: Fish Monitoring System
Created: 2026-02-15

This module defines schemas for daily fish health observations.

Dependencies:
    - pydantic: Data validation
    - datetime: Date handling

Example:
    >>> from app.schemas.observation import ObservationCreate
    >>> obs = ObservationCreate(
    ...     treatment_id=1,
    ...     overall_condition_score=4,
    ...     symptoms_lethargy=False,
    ...     treatments_completed=True
    ... )
"""

from pydantic import BaseModel, Field, field_validator
from datetime import date
from typing import Optional


class ObservationBase(BaseModel):
    """Base observation schema."""

    treatment_id: int = Field(..., gt=0)
    observation_date: date = Field(default_factory=date.today)
    overall_condition_score: Optional[int] = Field(None, ge=1, le=5)

    # Symptom checkboxes
    symptoms_lethargy: bool = False
    symptoms_loss_of_appetite: bool = False
    symptoms_spots: bool = False
    symptoms_fin_damage: bool = False
    symptoms_breathing_issues: bool = False
    symptoms_other: Optional[str] = None

    treatments_completed: bool = False
    notes: Optional[str] = None

    @field_validator('overall_condition_score')
    @classmethod
    def validate_score(cls, v: Optional[int]) -> Optional[int]:
        """Validate score is between 1 and 5."""
        if v is not None and not (1 <= v <= 5):
            raise ValueError("Condition score must be between 1 and 5")
        return v


class ObservationCreate(ObservationBase):
    """
    Schema for creating a daily observation.

    Example:
        >>> obs = ObservationCreate(
        ...     treatment_id=1,
        ...     observation_date=date.today(),
        ...     overall_condition_score=3,
        ...     symptoms_loss_of_appetite=True,
        ...     symptoms_spots=True,
        ...     treatments_completed=True,
        ...     notes="Some fish not eating well"
        ... )
    """
    pass


class ObservationUpdate(BaseModel):
    """
    Schema for updating an observation.

    All fields optional for partial updates.

    Example:
        >>> update = ObservationUpdate(
        ...     overall_condition_score=4,
        ...     notes="Improvement noted"
        ... )
    """

    overall_condition_score: Optional[int] = Field(None, ge=1, le=5)
    symptoms_lethargy: Optional[bool] = None
    symptoms_loss_of_appetite: Optional[bool] = None
    symptoms_spots: Optional[bool] = None
    symptoms_fin_damage: Optional[bool] = None
    symptoms_breathing_issues: Optional[bool] = None
    symptoms_other: Optional[str] = None
    treatments_completed: Optional[bool] = None
    notes: Optional[str] = None


class ObservationResponse(ObservationBase):
    """
    Schema for observation in API responses.

    Example:
        >>> {
        ...     "id": 1,
        ...     "treatment_id": 1,
        ...     "observation_date": "2026-02-15",
        ...     "overall_condition_score": 4,
        ...     "has_symptoms": false,
        ...     "treatments_completed": true
        ... }
    """

    id: int
    created_at: Optional[date] = None

    class Config:
        """Pydantic config for ORM mode."""
        from_attributes = True


class ObservationWithSummary(ObservationResponse):
    """
    Extended observation with computed fields.

    Example:
        >>> {
        ...     "id": 1,
        ...     "overall_condition_score": 4,
        ...     "has_symptoms": true,
        ...     "symptom_count": 2,
        ...     "score_description": "Good"
        ... }
    """

    has_symptoms: bool = False
    symptom_count: int = 0
    score_description: str = ""


class ObservationList(BaseModel):
    """
    Schema for list of observations.

    Example:
        >>> {
        ...     "treatment_id": 1,
        ...     "total": 7,
        ...     "observations": [...]
        ... }
    """

    treatment_id: int
    total: int
    observations: list[ObservationResponse]


class DailyChecklistItem(BaseModel):
    """
    Schema for daily checklist items (for n8n/WhatsApp).

    Simplified format for mobile quick entry.

    Example:
        >>> {
        ...     "treatment_id": 1,
        ...     "fish_name": "Betta splendens",
        ...     "drugs_to_administer": ["Methylene Blue 2.5mg/L"],
        ...     "current_day": 3
        ... }
    """

    treatment_id: int
    fish_name: str
    source: str
    drugs_to_administer: list[str]
    current_day: int
