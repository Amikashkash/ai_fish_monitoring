"""Schemas for Excel import functionality."""

from datetime import date as Date
from typing import List, Optional
from pydantic import BaseModel, Field


class ExtractedFishSpecies(BaseModel):
    """Schema for a fish species extracted from Excel."""
    scientific_name: Optional[str] = Field(None, description="Scientific (Latin) name of the fish")
    common_name: Optional[str] = Field(None, description="Common name of the fish")
    quantity: int = Field(..., description="Number of fish")
    size: Optional[str] = Field(None, description="Size description (e.g., '3-4cm', 'adult')")
    price_per_unit: Optional[float] = Field(None, description="Price per individual fish")
    total_price: Optional[float] = Field(None, description="Total price for this species")
    notes: Optional[str] = Field(None, description="Additional notes")


class ExcelExtractionResult(BaseModel):
    """Schema for AI extraction result from Excel file."""
    # Supplier information
    supplier_name: Optional[str] = Field(None, description="Name of the fish supplier")
    source_country: Optional[str] = Field(None, description="Country of origin")

    # Shipment information
    shipment_date: Optional[Date] = Field(None, description="Date of shipment")
    expected_arrival: Optional[Date] = Field(None, description="Expected arrival date")
    invoice_number: Optional[str] = Field(None, description="Invoice or proforma number")
    total_boxes: Optional[int] = Field(None, description="Total number of boxes/packages")

    # Fish species list
    fish_species: List[ExtractedFishSpecies] = Field(default_factory=list, description="List of fish species in shipment")

    # Additional information
    additional_notes: Optional[str] = Field(None, description="Any other relevant information")
    confidence: str = Field(..., description="AI confidence level: high/medium/low")

    # Metadata
    file_name: Optional[str] = Field(None, description="Original filename")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    extraction_method: str = Field(default="ai_powered", description="Method used for extraction")


class ExcelExtractionValidation(BaseModel):
    """Schema for validation results of extracted data."""
    errors: List[str] = Field(default_factory=list, description="Critical errors that prevent import")
    warnings: List[str] = Field(default_factory=list, description="Non-critical warnings")
    is_valid: bool = Field(..., description="Whether data is valid for import")


class ExcelImportResponse(BaseModel):
    """Schema for Excel import API response."""
    success: bool = Field(..., description="Whether extraction was successful")
    data: Optional[ExcelExtractionResult] = Field(None, description="Extracted data")
    validation: Optional[ExcelExtractionValidation] = Field(None, description="Validation results")
    error: Optional[str] = Field(None, description="Error message if extraction failed")


class ShipmentFromExcelCreate(BaseModel):
    """Schema for creating a shipment from extracted Excel data."""
    # Use extracted data to populate shipment
    supplier_name: str = Field(..., description="Supplier name")
    source: str = Field(..., description="Source country")
    date: Date = Field(..., description="Shipment date")
    expected_arrival: Optional[Date] = Field(None, description="Expected arrival date")
    invoice_number: Optional[str] = Field(None, description="Invoice/proforma number")

    # Fish species from Excel
    fish_species: List[ExtractedFishSpecies] = Field(..., description="Fish species list")

    # Additional fields
    total_boxes: Optional[int] = Field(None, description="Total boxes")
    notes: Optional[str] = Field(None, description="Additional notes")
