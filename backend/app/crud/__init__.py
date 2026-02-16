"""CRUD operations for database models."""

# Import all CRUD modules for easy access
from app.crud import shipment
from app.crud import treatment
from app.crud import observation
from app.crud import followup
from app.crud import drug_protocol
from app.crud import ai_knowledge

__all__ = [
    "shipment",
    "treatment",
    "observation",
    "followup",
    "drug_protocol",
    "ai_knowledge",
]
