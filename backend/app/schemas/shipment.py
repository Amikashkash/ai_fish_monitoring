"""
Filename: shipment.py
Purpose: Pydantic schemas for shipment API validation
Author: Fish Monitoring System
Created: 2026-02-15

This module defines Pydantic schemas for validating shipment data
in API requests and responses.

Dependencies:
    - pydantic: Data validation
    - datetime: Date handling

Example:
    >>> from app.schemas.shipment import ShipmentCreate
    >>> shipment = ShipmentCreate(
    ...     scientific_name="Betta splendens",
    ...     common_name="Siamese Fighting Fish",
    ...     source="Thailand",
    ...     quantity=50,
    ...     aquarium_volume_liters=200
    ... )
"""

from pydantic import BaseModel, Field, field_validator
from datetime import date
from typing import Optional
from decimal import Decimal


class ShipmentBase(BaseModel):
    """Base shipment schema with common fields."""

    scientific_name: str = Field(..., min_length=1, max_length=200)
    common_name: str = Field(..., min_length=1, max_length=200)
    source: str = Field(..., min_length=1, max_length=100)
    quantity: int = Field(..., gt=0, description="Number of fish (must be positive)")
    fish_size: Optional[str] = Field(None, max_length=50)
    aquarium_volume_liters: int = Field(..., gt=0, description="Tank volume in liters")
    price_per_fish: Optional[Decimal] = Field(None, ge=0)
    total_price: Optional[Decimal] = Field(None, ge=0)

    @field_validator('source')
    @classmethod
    def validate_source(cls, v: str) -> str:
        """Capitalize source country name."""
        return v.title()


class ShipmentCreate(ShipmentBase):
    """
    Schema for creating a new shipment.

    Used in POST /api/shipments endpoint.

    Example:
        >>> shipment = ShipmentCreate(
        ...     date=date.today(),
        ...     scientific_name="Paracheirodon innesi",
        ...     common_name="Neon Tetra",
        ...     source="Singapore",
        ...     quantity=100,
        ...     aquarium_volume_liters=500,
        ...     price_per_fish=0.50
        ... )
    """

    date: date = Field(default_factory=date.today, description="Shipment arrival date")


class ShipmentUpdate(BaseModel):
    """
    Schema for updating an existing shipment.

    All fields are optional for partial updates.

    Example:
        >>> update = ShipmentUpdate(quantity=45)  # Update only quantity
    """

    scientific_name: Optional[str] = Field(None, min_length=1, max_length=200)
    common_name: Optional[str] = Field(None, min_length=1, max_length=200)
    source: Optional[str] = Field(None, min_length=1, max_length=100)
    quantity: Optional[int] = Field(None, gt=0)
    fish_size: Optional[str] = Field(None, max_length=50)
    aquarium_volume_liters: Optional[int] = Field(None, gt=0)
    price_per_fish: Optional[Decimal] = Field(None, ge=0)
    total_price: Optional[Decimal] = Field(None, ge=0)


class ShipmentResponse(ShipmentBase):
    """
    Schema for shipment API responses.

    Includes computed fields like ID and density.

    Example:
        Response from GET /api/shipments/1:
        >>> {
        ...     "id": 1,
        ...     "date": "2026-02-15",
        ...     "scientific_name": "Betta splendens",
        ...     "density": 0.25,
        ...     ...
        ... }
    """

    id: int
    date: date
    density: Optional[Decimal] = Field(None, description="Auto-calculated fish per liter")
    created_at: Optional[date] = None

    class Config:
        """Pydantic config for ORM mode."""
        from_attributes = True  # Allows loading from SQLAlchemy models


class ShipmentWithTreatments(ShipmentResponse):
    """
    Extended shipment response with treatment information.

    Used when fetching shipment details with related treatments.

    Example:
        >>> {
        ...     "id": 1,
        ...     "scientific_name": "Betta splendens",
        ...     "treatment_count": 2,
        ...     "active_treatment": true
        ... }
    """

    treatment_count: int = 0
    has_active_treatment: bool = False


class ShipmentList(BaseModel):
    """
    Schema for paginated list of shipments.

    Example:
        >>> {
        ...     "total": 50,
        ...     "page": 1,
        ...     "page_size": 20,
        ...     "shipments": [...]
        ... }
    """

    total: int
    page: int = 1
    page_size: int = 20
    shipments: list[ShipmentResponse]
