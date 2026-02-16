"""
Filename: recommendation.py
Purpose: Pydantic schemas for AI recommendation responses
Author: Fish Monitoring System
Created: 2026-02-15

This module defines schemas for AI-generated recommendations
and supplier scoring.

Dependencies:
    - pydantic: Data validation

Example:
    >>> from app.schemas.recommendation import PreShipmentAdvice
    >>> advice = PreShipmentAdvice(
    ...     confidence="high",
    ...     success_rate=92.5,
    ...     sample_size=10,
    ...     recommendation="Highly recommended based on 10 successful shipments"
    ... )
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from decimal import Decimal


class PreShipmentAdvice(BaseModel):
    """
    Schema for pre-shipment AI advice.

    Returned when user queries about ordering a specific fish
    from a specific source before placing the order.

    Example:
        >>> {
        ...     "confidence": "high",
        ...     "success_rate": 92.5,
        ...     "sample_size": 10,
        ...     "recommendation": "Safe to order! 92.5% success rate",
        ...     "suggested_protocol": {...}
        ... }
    """

    confidence: str = Field(
        ...,
        pattern="^(high|medium|low|no_data)$",
        description="Confidence level based on historical data"
    )
    success_rate: Optional[Decimal] = Field(
        None,
        ge=0,
        le=100,
        description="Historical success rate percentage"
    )
    sample_size: int = Field(
        default=0,
        ge=0,
        description="Number of previous shipments"
    )
    recommendation: str = Field(
        ...,
        description="AI-generated recommendation text"
    )
    suggested_protocol: Optional[Dict[str, Any]] = Field(
        None,
        description="Recommended drug protocol if available"
    )


class InitialProtocolRecommendation(BaseModel):
    """
    Schema for initial treatment protocol recommendation.

    Provided on day 1 when starting treatment for a new shipment.

    Example:
        >>> {
        ...     "confidence": "medium",
        ...     "success_rate": 85.0,
        ...     "sample_size": 5,
        ...     "recommended_drugs": [
        ...         {"drug_name": "Methylene Blue", "dosage": 2.5},
        ...         {"drug_name": "Aquarium Salt", "dosage": 1.0}
        ...     ],
        ...     "treatment_duration_days": 7,
        ...     "reasoning": "Based on 5 previous shipments..."
        ... }
    """

    confidence: str = Field(..., pattern="^(high|medium|low|no_data)$")
    success_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    sample_size: int = Field(default=0, ge=0)
    recommended_drugs: List[Dict[str, Any]] = Field(default_factory=list)
    treatment_duration_days: Optional[int] = None
    reasoning: str = ""
    density_warning: Optional[str] = None


class SupplierScore(BaseModel):
    """
    Schema for supplier performance scoring.

    Example:
        >>> {
        ...     "source": "Thailand",
        ...     "shipment_count": 15,
        ...     "avg_success_rate": 91.5,
        ...     "total_fish": 750,
        ...     "species_count": 8,
        ...     "rating": "excellent",
        ...     "recommendation": "Highly recommended supplier"
        ... }
    """

    source: str
    shipment_count: int = 0
    avg_success_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    total_fish: int = 0
    species_count: int = 0
    rating: str = Field(
        default="no_data",
        pattern="^(excellent|good|fair|poor|insufficient_data|no_data)$"
    )
    recommendation: str = ""


class SupplierComparison(BaseModel):
    """
    Schema for comparing multiple suppliers.

    Example:
        >>> {
        ...     "suppliers": [
        ...         {"source": "Thailand", "avg_success_rate": 92.5},
        ...         {"source": "Sri Lanka", "avg_success_rate": 88.0}
        ...     ],
        ...     "best_source": "Thailand",
        ...     "comparison_summary": "Thailand has 4.5% higher success rate"
        ... }
    """

    suppliers: List[SupplierScore]
    best_source: Optional[str] = None
    comparison_summary: str = ""


class SpeciesBestSource(BaseModel):
    """
    Schema for best source recommendation for a specific species.

    Example:
        >>> {
        ...     "scientific_name": "Betta splendens",
        ...     "best_source": "Thailand",
        ...     "success_rate": 94.0,
        ...     "shipment_count": 12,
        ...     "reasoning": "Thailand has highest success rate for this species"
        ... }
    """

    scientific_name: str
    best_source: Optional[str] = None
    success_rate: Optional[Decimal] = None
    shipment_count: int = 0
    reasoning: str = ""
    alternative_sources: List[Dict[str, Any]] = Field(default_factory=list)


class TreatmentModificationAdvice(BaseModel):
    """
    Schema for advice on modifying an ongoing treatment.

    Example:
        >>> {
        ...     "should_modify": true,
        ...     "modification_type": "extend_treatment",
        ...     "reasoning": "Symptoms persist, recommend extending 3 days",
        ...     "suggested_changes": [...]
        ... }
    """

    should_modify: bool
    modification_type: str = Field(
        default="no_change",
        pattern="^(extend_treatment|change_drugs|adjust_dosage|add_drug|no_change)$"
    )
    reasoning: str = ""
    suggested_changes: List[Dict[str, Any]] = Field(default_factory=list)


class AIInsights(BaseModel):
    """
    Schema for general AI insights from data analysis.

    Example:
        >>> {
        ...     "total_shipments_analyzed": 50,
        ...     "overall_success_rate": 89.5,
        ...     "key_insights": [
        ...         "High density shipments require extended treatment",
        ...         "Thailand sources have best success rates"
        ...     ],
        ...     "recommendations": [...]
        ... }
    """

    total_shipments_analyzed: int = 0
    overall_success_rate: Optional[Decimal] = None
    key_insights: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    patterns_discovered: List[Dict[str, Any]] = Field(default_factory=list)
