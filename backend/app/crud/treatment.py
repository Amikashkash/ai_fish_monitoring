"""
Filename: treatment.py
Purpose: CRUD operations for treatment database records
Author: Fish Monitoring System
Created: 2026-02-15

This module provides database operations for treatments and treatment drugs.

Dependencies:
    - sqlalchemy.orm: Database session
    - app.models.treatment: Treatment, TreatmentDrug models
    - app.schemas.treatment: Treatment schemas

Example:
    >>> from app.crud import treatment
    >>> new_treatment = treatment.create_treatment(db, treatment_data)
    >>> active = treatment.get_active_treatments(db)
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.models.treatment import Treatment, TreatmentDrug
from app.schemas.treatment import TreatmentCreate, TreatmentUpdate


def create_treatment(
    db: Session,
    treatment: TreatmentCreate
) -> Treatment:
    """
    Create a new treatment with associated drugs.

    Args:
        db: Database session
        treatment: Treatment creation schema

    Returns:
        Created Treatment object with drugs

    Example:
        >>> treatment_data = TreatmentCreate(
        ...     shipment_id=1,
        ...     start_date=date.today(),
        ...     drugs=[
        ...         {"drug_protocol_id": 1, "actual_dosage": 2.5}
        ...     ]
        ... )
        >>> new_treatment = create_treatment(db, treatment_data)
    """
    # Extract drugs list
    drugs_data = treatment.drugs
    treatment_dict = treatment.model_dump(exclude={"drugs"})

    # Create treatment
    db_treatment = Treatment(**treatment_dict)
    db.add(db_treatment)
    db.flush()  # Get ID without committing

    # Add drugs
    for drug_data in drugs_data:
        db_drug = TreatmentDrug(
            treatment_id=db_treatment.id,
            **drug_data.model_dump()
        )
        db.add(db_drug)

    db.commit()
    db.refresh(db_treatment)
    return db_treatment


def get_treatment(db: Session, treatment_id: int) -> Optional[Treatment]:
    """
    Get a treatment by ID.

    Args:
        db: Database session
        treatment_id: Treatment ID

    Returns:
        Treatment object or None

    Example:
        >>> treatment = get_treatment(db, 1)
        >>> print(len(treatment.treatment_drugs))
    """
    return db.query(Treatment).filter(Treatment.id == treatment_id).first()


def get_treatments(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> List[Treatment]:
    """
    Get list of treatments with pagination.

    Args:
        db: Database session
        skip: Records to skip
        limit: Maximum records

    Returns:
        List of Treatment objects

    Example:
        >>> treatments = get_treatments(db, skip=0, limit=20)
    """
    return db.query(Treatment).offset(skip).limit(limit).all()


def get_treatments_by_shipment(
    db: Session,
    shipment_id: int
) -> List[Treatment]:
    """
    Get all treatments for a specific shipment.

    Args:
        db: Database session
        shipment_id: Shipment ID

    Returns:
        List of Treatment objects

    Example:
        >>> treatments = get_treatments_by_shipment(db, 1)
    """
    return db.query(Treatment).filter(
        Treatment.shipment_id == shipment_id
    ).all()


def get_active_treatments(db: Session) -> List[Treatment]:
    """
    Get all currently active treatments.

    Args:
        db: Database session

    Returns:
        List of active Treatment objects

    Example:
        >>> active = get_active_treatments(db)
        >>> print(f"Active treatments: {len(active)}")
    """
    return db.query(Treatment).filter(
        Treatment.status == "active"
    ).all()


def get_treatments_by_status(
    db: Session,
    status: str
) -> List[Treatment]:
    """
    Get treatments filtered by status.

    Args:
        db: Database session
        status: Treatment status (active, completed, modified)

    Returns:
        List of Treatment objects

    Example:
        >>> completed = get_treatments_by_status(db, "completed")
    """
    return db.query(Treatment).filter(Treatment.status == status).all()


def get_treatments_ending_on_date(
    db: Session,
    end_date: date
) -> List[Treatment]:
    """
    Get treatments ending on a specific date.

    Args:
        db: Database session
        end_date: Date to check

    Returns:
        List of Treatment objects ending on that date

    Example:
        >>> ending_today = get_treatments_ending_on_date(db, date.today())
    """
    return db.query(Treatment).filter(
        Treatment.end_date == end_date,
        Treatment.status == "active"
    ).all()


def update_treatment(
    db: Session,
    treatment_id: int,
    treatment_update: TreatmentUpdate
) -> Optional[Treatment]:
    """
    Update an existing treatment.

    Args:
        db: Database session
        treatment_id: Treatment ID
        treatment_update: Update schema

    Returns:
        Updated Treatment or None

    Example:
        >>> update = TreatmentUpdate(
        ...     end_date=date.today(),
        ...     status="completed"
        ... )
        >>> updated = update_treatment(db, 1, update)
    """
    db_treatment = get_treatment(db, treatment_id)
    if not db_treatment:
        return None

    update_data = treatment_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_treatment, field, value)

    db.commit()
    db.refresh(db_treatment)
    return db_treatment


def complete_treatment(
    db: Session,
    treatment_id: int,
    end_date: Optional[date] = None
) -> Optional[Treatment]:
    """
    Mark a treatment as completed.

    Args:
        db: Database session
        treatment_id: Treatment ID
        end_date: End date (default: today)

    Returns:
        Updated Treatment or None

    Example:
        >>> completed = complete_treatment(db, 1)
        >>> print(completed.status)
        'completed'
    """
    if end_date is None:
        end_date = date.today()

    return update_treatment(
        db,
        treatment_id,
        TreatmentUpdate(end_date=end_date, status="completed")
    )


def add_drug_to_treatment(
    db: Session,
    treatment_id: int,
    drug_protocol_id: int,
    actual_dosage: Optional[float] = None,
    actual_frequency: Optional[str] = None
) -> Optional[TreatmentDrug]:
    """
    Add a drug to an existing treatment.

    Args:
        db: Database session
        treatment_id: Treatment ID
        drug_protocol_id: Drug protocol ID
        actual_dosage: Actual dosage used
        actual_frequency: Actual frequency

    Returns:
        Created TreatmentDrug or None

    Example:
        >>> drug = add_drug_to_treatment(db, 1, 2, 1.0, "twice daily")
    """
    # Verify treatment exists
    treatment = get_treatment(db, treatment_id)
    if not treatment:
        return None

    db_drug = TreatmentDrug(
        treatment_id=treatment_id,
        drug_protocol_id=drug_protocol_id,
        actual_dosage=actual_dosage,
        actual_frequency=actual_frequency
    )
    db.add(db_drug)
    db.commit()
    db.refresh(db_drug)
    return db_drug


def delete_treatment(db: Session, treatment_id: int) -> bool:
    """
    Delete a treatment record.

    Args:
        db: Database session
        treatment_id: Treatment ID

    Returns:
        True if deleted, False if not found

    Example:
        >>> deleted = delete_treatment(db, 1)
    """
    db_treatment = get_treatment(db, treatment_id)
    if not db_treatment:
        return False

    db.delete(db_treatment)
    db.commit()
    return True


def count_treatments(db: Session) -> int:
    """
    Count total treatments.

    Args:
        db: Database session

    Returns:
        Total number of treatments

    Example:
        >>> total = count_treatments(db)
    """
    return db.query(Treatment).count()


def count_active_treatments(db: Session) -> int:
    """
    Count currently active treatments.

    Args:
        db: Database session

    Returns:
        Number of active treatments

    Example:
        >>> active_count = count_active_treatments(db)
    """
    return db.query(Treatment).filter(Treatment.status == "active").count()
