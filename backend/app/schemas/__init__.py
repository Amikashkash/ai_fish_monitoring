"""Pydantic schemas for API validation."""

from app.schemas.shipment import (
    ShipmentCreate,
    ShipmentUpdate,
    ShipmentResponse,
    ShipmentWithTreatments,
    ShipmentList
)

from app.schemas.treatment import (
    TreatmentCreate,
    TreatmentUpdate,
    TreatmentResponse,
    TreatmentWithDetails,
    TreatmentDrugCreate,
    TreatmentDrugResponse,
    TreatmentList
)

from app.schemas.observation import (
    ObservationCreate,
    ObservationUpdate,
    ObservationResponse,
    ObservationWithSummary,
    ObservationList,
    DailyChecklistItem
)

from app.schemas.followup import (
    FollowupCreate,
    FollowupUpdate,
    FollowupResponse,
    FollowupWithDetails,
    FollowupList
)

from app.schemas.drug_protocol import (
    DrugProtocolCreate,
    DrugProtocolUpdate,
    DrugProtocolResponse,
    DrugProtocolWithUsage,
    DrugProtocolList
)

from app.schemas.recommendation import (
    PreShipmentAdvice,
    InitialProtocolRecommendation,
    SupplierScore,
    SupplierComparison,
    SpeciesBestSource,
    TreatmentModificationAdvice,
    AIInsights
)

__all__ = [
    # Shipment schemas
    "ShipmentCreate",
    "ShipmentUpdate",
    "ShipmentResponse",
    "ShipmentWithTreatments",
    "ShipmentList",
    # Treatment schemas
    "TreatmentCreate",
    "TreatmentUpdate",
    "TreatmentResponse",
    "TreatmentWithDetails",
    "TreatmentDrugCreate",
    "TreatmentDrugResponse",
    "TreatmentList",
    # Observation schemas
    "ObservationCreate",
    "ObservationUpdate",
    "ObservationResponse",
    "ObservationWithSummary",
    "ObservationList",
    "DailyChecklistItem",
    # Followup schemas
    "FollowupCreate",
    "FollowupUpdate",
    "FollowupResponse",
    "FollowupWithDetails",
    "FollowupList",
    # Drug protocol schemas
    "DrugProtocolCreate",
    "DrugProtocolUpdate",
    "DrugProtocolResponse",
    "DrugProtocolWithUsage",
    "DrugProtocolList",
    # Recommendation schemas
    "PreShipmentAdvice",
    "InitialProtocolRecommendation",
    "SupplierScore",
    "SupplierComparison",
    "SpeciesBestSource",
    "TreatmentModificationAdvice",
    "AIInsights",
]
