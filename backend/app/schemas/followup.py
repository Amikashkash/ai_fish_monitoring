"""
Filename: followup.py
Purpose: Pydantic schemas for follow-up assessment validation
Author: Fish Monitoring System
Created: 2026-02-15

This module defines schemas for 5-day post-treatment follow-up assessments.

Dependencies:
    - pydantic: Data validation
    - datetime: Date handling

Example:
    >>> from app.schemas.followup import FollowupCreate
    >>> followup = FollowupCreate(
    ...     treatment_id=1,
    ...     stability_score=5,
    ...     symptoms_returned=False,
    ...     survival_count=48,
    ...     success_rate=96.0
    ... )
"""

from pydantic import BaseModel, Field, field_validator
from datetime import date
from typing import Optional
from decimal import Decimal


class FollowupBase(BaseModel):
    """Base follow-up assessment schema."""

    treatment_id: int = Field(..., gt=0)
    followup_date: date = Field(default_factory=date.today)
    stability_score: Optional[int] = Field(None, ge=1, le=5)
    symptoms_returned: bool = False
    returned_symptoms: Optional[str] = None
    survival_count: Optional[int] = Field(None, ge=0)
    success_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    recommendation: Optional[str] = None
    ai_learning_notes: Optional[str] = None

    @field_validator('stability_score')
    @classmethod
    def validate_score(cls, v: Optional[int]) -> Optional[int]:
        """Validate stability score is between 1 and 5."""
        if v is not None and not (1 <= v <= 5):
            raise ValueError("Stability score must be between 1 and 5")
        return v


class FollowupCreate(FollowupBase):
    """
    Schema for creating a follow-up assessment.

    Example:
        >>> followup = FollowupCreate(
        ...     treatment_id=1,
        ...     followup_date=date.today(),
        ...     stability_score=4,
        ...     symptoms_returned=False,
        ...     survival_count=47,
        ...     success_rate=94.0,
        ...     recommendation="Protocol effective, recommend for future"
        ... )
    """
    pass


class FollowupUpdate(BaseModel):
    """
    Schema for updating a follow-up assessment.

    Example:
        >>> update = FollowupUpdate(
        ...     ai_learning_notes="Updated with new insights"
        ... )
    """

    stability_score: Optional[int] = Field(None, ge=1, le=5)
    symptoms_returned: Optional[bool] = None
    returned_symptoms: Optional[str] = None
    survival_count: Optional[int] = Field(None, ge=0)
    success_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    recommendation: Optional[str] = None
    ai_learning_notes: Optional[str] = None


class FollowupResponse(FollowupBase):
    """
    Schema for follow-up in API responses.

    Example:
        >>> {
        ...     "id": 1,
        ...     "treatment_id": 1,
        ...     "followup_date": "2026-02-20",
        ...     "stability_score": 4,
        ...     "success_rate": 94.0,
        ...     "is_successful": true
        ... }
    """

    id: int
    created_at: Optional[date] = None

    class Config:
        """Pydantic config for ORM mode."""
        from_attributes = True


class FollowupWithDetails(FollowupResponse):
    """
    Extended follow-up with treatment and shipment details.

    Example:
        >>> {
        ...     "id": 1,
        ...     "treatment_id": 1,
        ...     "fish_species": "Betta splendens",
        ...     "source": "Thailand",
        ...     "original_quantity": 50,
        ...     "survival_count": 47,
        ...     "success_rate": 94.0,
        ...     "effectiveness": "excellent"
        ... }
    """

    fish_species: Optional[str] = None
    source: Optional[str] = None
    original_quantity: Optional[int] = None
    effectiveness: str = ""  # excellent, good, fair, poor


class FollowupList(BaseModel):
    """
    Schema for list of follow-up assessments.

    Example:
        >>> {
        ...     "total": 15,
        ...     "avg_success_rate": 88.5,
        ...     "followups": [...]
        ... }
    """

    total: int
    avg_success_rate: Optional[Decimal] = None
    followups: list[FollowupResponse]
