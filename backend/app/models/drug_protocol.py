"""
Filename: drug_protocol.py
Purpose: Drug protocol database model for treatment medications
Author: Fish Monitoring System
Created: 2026-02-15

This module defines the DrugProtocol ORM model for storing information
about medications used in fish treatments.

Dependencies:
    - sqlalchemy: ORM framework
    - app.config.database: Base class

Example:
    >>> from app.models.drug_protocol import DrugProtocol
    >>> protocol = DrugProtocol(
    ...     drug_name="Methylene Blue",
    ...     dosage_min=1.0,
    ...     dosage_max=5.0,
    ...     dosage_unit="mg/L",
    ...     frequency="once daily",
    ...     typical_treatment_period_days=7
    ... )
"""

from sqlalchemy import Column, Integer, String, DECIMAL, TIMESTAMP, func
from app.config.database import Base


class DrugProtocol(Base):
    """
    Represents a drug/medication protocol for fish treatment.

    Stores standard dosage information, frequency, and typical
    treatment duration for medications used in fish health management.

    Attributes:
        id: Unique protocol identifier (auto-generated)
        drug_name: Name of the medication (must be unique)
        dosage_min: Minimum recommended dosage
        dosage_max: Maximum recommended dosage
        dosage_unit: Unit of measurement (mg/L, ml/10L, etc.)
        frequency: How often to administer (once daily, twice daily, etc.)
        typical_treatment_period_days: Standard treatment duration in days
        notes: Additional information or special instructions
        created_at: Timestamp when protocol was created

    Example:
        >>> protocol = DrugProtocol(
        ...     drug_name="Malachite Green",
        ...     dosage_min=0.05,
        ...     dosage_max=0.15,
        ...     dosage_unit="mg/L",
        ...     frequency="every other day",
        ...     typical_treatment_period_days=3,
        ...     notes="Avoid with sensitive scaleless fish"
        ... )
    """

    __tablename__ = "drug_protocols"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    drug_name = Column(String, nullable=False, unique=True)
    dosage_min = Column(DECIMAL(10, 2), nullable=True)
    dosage_max = Column(DECIMAL(10, 2), nullable=True)
    dosage_unit = Column(String, nullable=True)
    frequency = Column(String, nullable=True)
    typical_treatment_period_days = Column(Integer, nullable=True)
    notes = Column(String, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    def __repr__(self) -> str:
        """String representation of drug protocol."""
        return (
            f"<DrugProtocol(id={self.id}, "
            f"drug='{self.drug_name}', "
            f"dosage={self.dosage_min}-{self.dosage_max} {self.dosage_unit})>"
        )
