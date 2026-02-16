"""
Filename: drug_protocol.py
Purpose: Pydantic schemas for drug protocol validation
Author: Fish Monitoring System
Created: 2026-02-15

This module defines schemas for drug/medication protocols.

Dependencies:
    - pydantic: Data validation

Example:
    >>> from app.schemas.drug_protocol import DrugProtocolCreate
    >>> protocol = DrugProtocolCreate(
    ...     drug_name="Methylene Blue",
    ...     dosage_min=1.0,
    ...     dosage_max=5.0,
    ...     dosage_unit="mg/L",
    ...     frequency="once daily"
    ... )
"""

from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal


class DrugProtocolBase(BaseModel):
    """Base drug protocol schema."""

    drug_name: str = Field(..., min_length=1, max_length=200)
    dosage_min: Optional[Decimal] = Field(None, ge=0)
    dosage_max: Optional[Decimal] = Field(None, ge=0)
    dosage_unit: Optional[str] = Field(None, max_length=50)
    frequency: Optional[str] = Field(None, max_length=100)
    typical_treatment_period_days: Optional[int] = Field(None, gt=0)
    notes: Optional[str] = None


class DrugProtocolCreate(DrugProtocolBase):
    """
    Schema for creating a new drug protocol.

    Example:
        >>> protocol = DrugProtocolCreate(
        ...     drug_name="Malachite Green",
        ...     dosage_min=0.05,
        ...     dosage_max=0.15,
        ...     dosage_unit="mg/L",
        ...     frequency="every other day",
        ...     typical_treatment_period_days=3,
        ...     notes="Avoid with scaleless fish"
        ... )
    """
    pass


class DrugProtocolUpdate(BaseModel):
    """
    Schema for updating a drug protocol.

    All fields optional for partial updates.

    Example:
        >>> update = DrugProtocolUpdate(
        ...     dosage_max=6.0,
        ...     notes="Updated maximum dosage"
        ... )
    """

    drug_name: Optional[str] = Field(None, min_length=1, max_length=200)
    dosage_min: Optional[Decimal] = Field(None, ge=0)
    dosage_max: Optional[Decimal] = Field(None, ge=0)
    dosage_unit: Optional[str] = Field(None, max_length=50)
    frequency: Optional[str] = Field(None, max_length=100)
    typical_treatment_period_days: Optional[int] = Field(None, gt=0)
    notes: Optional[str] = None


class DrugProtocolResponse(DrugProtocolBase):
    """
    Schema for drug protocol in API responses.

    Example:
        >>> {
        ...     "id": 1,
        ...     "drug_name": "Methylene Blue",
        ...     "dosage_min": 1.0,
        ...     "dosage_max": 5.0,
        ...     "dosage_unit": "mg/L",
        ...     "frequency": "once daily",
        ...     "dosage_display": "1.0-5.0 mg/L"
        ... }
    """

    id: int

    class Config:
        """Pydantic config for ORM mode."""
        from_attributes = True


class DrugProtocolWithUsage(DrugProtocolResponse):
    """
    Extended protocol with usage statistics.

    Example:
        >>> {
        ...     "id": 1,
        ...     "drug_name": "Methylene Blue",
        ...     "times_used": 25,
        ...     "avg_success_rate": 92.5
        ... }
    """

    times_used: int = 0
    avg_success_rate: Optional[Decimal] = None


class DrugProtocolList(BaseModel):
    """
    Schema for list of drug protocols.

    Example:
        >>> {
        ...     "total": 10,
        ...     "protocols": [...]
        ... }
    """

    total: int
    protocols: list[DrugProtocolResponse]
