"""Pydantic schemas for invoice (shipment header) API."""

from pydantic import BaseModel, Field
from datetime import date as Date
from typing import Optional, List
from decimal import Decimal


class InvoiceCreate(BaseModel):
    date: Date = Field(default_factory=Date.today)
    supplier_name: Optional[str] = Field(None, max_length=200)
    invoice_number: Optional[str] = Field(None, max_length=100)
    source: str = Field(default="", max_length=100)
    notes: Optional[str] = None


class InvoiceUpdate(BaseModel):
    date: Optional[Date] = None
    supplier_name: Optional[str] = None
    invoice_number: Optional[str] = None
    source: Optional[str] = None
    notes: Optional[str] = None


class FishItemCreate(BaseModel):
    """A single fish species being added to an invoice."""
    scientific_name: str = Field(..., min_length=1, max_length=200)
    common_name: Optional[str] = Field(None, max_length=200)
    quantity: int = Field(..., gt=0)
    fish_size: Optional[str] = Field(None, max_length=50)
    aquarium_number: Optional[str] = Field(None, max_length=50)
    aquarium_volume_liters: Optional[int] = Field(None, gt=0)
    price_per_fish: Optional[Decimal] = Field(None, ge=0)
    notes: Optional[str] = None
