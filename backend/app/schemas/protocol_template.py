"""Protocol template schemas for API validation."""

from datetime import datetime as DateTime
from typing import List, Optional
from pydantic import BaseModel, Field


# Drug within a protocol template
class ProtocolTemplateDrugBase(BaseModel):
    """Base schema for protocol template drug."""
    drug_protocol_id: int = Field(..., description="ID of the drug from drug_protocols table")
    dosage: str = Field(..., description="Specific dosage for this protocol (e.g., '5 gr / 100 liter')")
    frequency: str = Field(..., description="Frequency of administration (e.g., 'every day for 10 days')")
    sequence_order: int = Field(default=1, description="Order in which drugs should be administered")
    notes: Optional[str] = Field(None, description="Additional drug-specific notes")


class ProtocolTemplateDrugCreate(ProtocolTemplateDrugBase):
    """Schema for creating a protocol template drug."""
    pass


class ProtocolTemplateDrugResponse(ProtocolTemplateDrugBase):
    """Schema for protocol template drug response."""
    id: int
    protocol_template_id: int
    created_at: DateTime

    class Config:
        from_attributes = True


# Protocol Template
class ProtocolTemplateBase(BaseModel):
    """Base schema for protocol template."""
    name: str = Field(..., description="Unique name for the protocol")
    purpose: str = Field(..., description="Treatment purpose (e.g., 'bacterial infections')")
    duration_days: Optional[int] = Field(None, description="Treatment duration in days")
    special_instructions: Optional[str] = Field(None, description="Special instructions (e.g., 'reduce dosage by half after third day')")


class ProtocolTemplateCreate(ProtocolTemplateBase):
    """Schema for creating a protocol template."""
    drugs: List[ProtocolTemplateDrugCreate] = Field(..., description="List of drugs in this protocol")


class ProtocolTemplateUpdate(BaseModel):
    """Schema for updating a protocol template."""
    name: Optional[str] = None
    purpose: Optional[str] = None
    duration_days: Optional[int] = None
    special_instructions: Optional[str] = None
    drugs: Optional[List[ProtocolTemplateDrugCreate]] = None


class ProtocolTemplateResponse(ProtocolTemplateBase):
    """Schema for protocol template response."""
    id: int
    times_used: int
    successful_outcomes: int
    success_rate: Optional[float]
    created_at: DateTime
    updated_at: DateTime

    class Config:
        from_attributes = True


class ProtocolTemplateDetailResponse(ProtocolTemplateResponse):
    """Schema for detailed protocol template response with drugs."""
    drugs: List[ProtocolTemplateDrugResponse] = Field(default_factory=list)


class ProtocolTemplateWithDrugDetails(BaseModel):
    """Schema for protocol template with full drug information from view."""
    template_id: int
    template_name: str
    purpose: str
    duration_days: Optional[int]
    special_instructions: Optional[str]
    times_used: int
    successful_outcomes: int
    success_rate: Optional[float]
    created_at: DateTime
    updated_at: DateTime
    drugs: List[dict]  # JSON array from the view

    class Config:
        from_attributes = True


class ProtocolTemplateUsageUpdate(BaseModel):
    """Schema for updating protocol template usage statistics."""
    was_successful: bool = Field(..., description="Whether the treatment was successful")
