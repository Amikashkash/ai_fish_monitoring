"""
Filename: treatment.py
Purpose: Treatment and TreatmentDrug models for fish health protocols
Author: Fish Monitoring System
Created: 2026-02-15

This module defines Treatment and TreatmentDrug models.
Treatment represents a treatment session for a shipment.
TreatmentDrug links treatments to specific drugs used.

Dependencies:
    - sqlalchemy: ORM framework
    - app.config.database: Base class

Example:
    >>> from app.models.treatment import Treatment, TreatmentDrug
    >>> treatment = Treatment(
    ...     shipment_id=1,
    ...     start_date=date.today(),
    ...     status="active"
    ... )
"""

from sqlalchemy import Column, Integer, String, Date, DECIMAL, TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import relationship
from app.config.database import Base


class Treatment(Base):
    """
    Represents a treatment protocol session for a fish shipment.

    Each treatment is linked to a shipment and tracks the period
    during which fish are being medicated and monitored.

    Attributes:
        id: Unique treatment identifier (auto-generated)
        shipment_id: Reference to the shipment being treated
        start_date: Date treatment began
        end_date: Date treatment completed (null if ongoing)
        status: Current status (active, completed, modified)
        created_at: Timestamp when treatment record was created
        shipment: Relationship to Shipment model
        treatment_drugs: Relationship to TreatmentDrug records

    Example:
        >>> treatment = Treatment(
        ...     shipment_id=1,
        ...     start_date=date(2026, 2, 15),
        ...     status="active"
        ... )
    """

    __tablename__ = "treatments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    shipment_id = Column(Integer, ForeignKey("shipments.id", ondelete="CASCADE"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    status = Column(String, nullable=False, default="active", index=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    shipment = relationship("Shipment", backref="treatments")
    treatment_drugs = relationship("TreatmentDrug", back_populates="treatment", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        """String representation of treatment."""
        return (
            f"<Treatment(id={self.id}, "
            f"shipment_id={self.shipment_id}, "
            f"status='{self.status}')>"
        )


class TreatmentDrug(Base):
    """
    Links treatments to specific drugs used with actual dosages.

    This is a many-to-many relationship table between Treatment
    and DrugProtocol, storing the actual dosage used for each drug
    in a specific treatment.

    Attributes:
        id: Unique record identifier (auto-generated)
        treatment_id: Reference to the treatment
        drug_protocol_id: Reference to the drug protocol used
        actual_dosage: The actual dosage administered
        actual_frequency: The actual frequency of administration
        notes: Additional notes about drug usage
        treatment: Relationship to Treatment model
        drug_protocol: Relationship to DrugProtocol model

    Example:
        >>> treatment_drug = TreatmentDrug(
        ...     treatment_id=1,
        ...     drug_protocol_id=2,
        ...     actual_dosage=2.5,
        ...     actual_frequency="once daily",
        ...     notes="Administered in morning"
        ... )
    """

    __tablename__ = "treatment_drugs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    treatment_id = Column(Integer, ForeignKey("treatments.id", ondelete="CASCADE"), nullable=False)
    drug_protocol_id = Column(Integer, ForeignKey("drug_protocols.id"), nullable=False)
    actual_dosage = Column(DECIMAL(10, 2), nullable=True)
    actual_frequency = Column(String, nullable=True)
    notes = Column(String, nullable=True)

    # Relationships
    treatment = relationship("Treatment", back_populates="treatment_drugs")
    drug_protocol = relationship("DrugProtocol")

    def __repr__(self) -> str:
        """String representation of treatment drug."""
        return (
            f"<TreatmentDrug(id={self.id}, "
            f"treatment_id={self.treatment_id}, "
            f"drug_id={self.drug_protocol_id})>"
        )
