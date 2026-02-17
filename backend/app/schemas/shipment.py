"""
Filename: shipment.py
Purpose: Pydantic schemas for shipment API validation
Author: Fish Monitoring System
Created: 2026-02-15
"""

from pydantic import BaseModel, Field, field_validator
from datetime import date as Date
from typing import Optional
from decimal import Decimal


class ShipmentBase(BaseModel):
    """Base shipment schema with common fields."""

    scientific_name: str = Field(..., min_length=1, max_length=200)
    common_name: Optional[str] = Field(None, max_length=200)
    source: str = Field(..., min_length=1, max_length=100)
    quantity: int = Field(..., gt=0, description="Number of fish")
    fish_size: Optional[str] = Field(None, max_length=50)
    aquarium_volume_liters: Optional[int] = Field(None, gt=0, description="Tank volume in liters")
    aquarium_number: Optional[str] = Field(None, max_length=50, description="Tank identifier, e.g. 'Tank 3'")
    price_per_fish: Optional[Decimal] = Field(None, ge=0)
    total_price: Optional[Decimal] = Field(None, ge=0)
    notes: Optional[str] = None
    invoice_number: Optional[str] = Field(None, max_length=100)
    supplier_name: Optional[str] = Field(None, max_length=200)

    @field_validator('source')
    @classmethod
    def validate_source(cls, v: str) -> str:
        """Capitalize source country name."""
        return v.title()


class ShipmentCreate(ShipmentBase):
    """Schema for creating a new shipment."""

    date: Date = Field(default_factory=Date.today, description="Shipment arrival date")


class ShipmentUpdate(BaseModel):
    """Schema for updating an existing shipment. All fields optional."""

    scientific_name: Optional[str] = Field(None, min_length=1, max_length=200)
    common_name: Optional[str] = Field(None, max_length=200)
    source: Optional[str] = Field(None, min_length=1, max_length=100)
    quantity: Optional[int] = Field(None, gt=0)
    fish_size: Optional[str] = Field(None, max_length=50)
    aquarium_volume_liters: Optional[int] = Field(None, gt=0)
    aquarium_number: Optional[str] = Field(None, max_length=50)
    price_per_fish: Optional[Decimal] = Field(None, ge=0)
    total_price: Optional[Decimal] = Field(None, ge=0)
    notes: Optional[str] = None
    invoice_number: Optional[str] = Field(None, max_length=100)
    supplier_name: Optional[str] = Field(None, max_length=200)


class ShipmentResponse(ShipmentBase):
    """Schema for shipment API responses."""

    id: int
    date: Date
    density: Optional[Decimal] = Field(None, description="Auto-calculated fish per liter")
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


class ShipmentWithTreatments(ShipmentResponse):
    """Extended shipment response with treatment information."""

    treatment_count: int = 0
    has_active_treatment: bool = False


class ShipmentList(BaseModel):
    """Schema for paginated list of shipments."""

    total: int
    page: int = 1
    page_size: int = 20
    shipments: list[ShipmentResponse]
