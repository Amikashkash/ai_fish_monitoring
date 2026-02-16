"""
Filename: drug_protocol.py
Purpose: CRUD operations for drug protocol records
Author: Fish Monitoring System
Created: 2026-02-15

This module provides database operations for drug/medication protocols.

Dependencies:
    - sqlalchemy.orm: Database session
    - app.models.drug_protocol: DrugProtocol model
    - app.schemas.drug_protocol: DrugProtocol schemas

Example:
    >>> from app.crud import drug_protocol
    >>> protocol = drug_protocol.get_protocol_by_name(db, "Methylene Blue")
"""

from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.drug_protocol import DrugProtocol
from app.schemas.drug_protocol import DrugProtocolCreate, DrugProtocolUpdate


def create_drug_protocol(
    db: Session,
    protocol: DrugProtocolCreate
) -> DrugProtocol:
    """
    Create a new drug protocol.

    Args:
        db: Database session
        protocol: DrugProtocol creation schema

    Returns:
        Created DrugProtocol object

    Example:
        >>> protocol_data = DrugProtocolCreate(
        ...     drug_name="Copper Sulfate",
        ...     dosage_min=0.15,
        ...     dosage_max=0.20,
        ...     dosage_unit="mg/L",
        ...     frequency="continuous"
        ... )
        >>> protocol = create_drug_protocol(db, protocol_data)
    """
    db_protocol = DrugProtocol(**protocol.model_dump())
    db.add(db_protocol)
    db.commit()
    db.refresh(db_protocol)
    return db_protocol


def get_drug_protocol(
    db: Session,
    protocol_id: int
) -> Optional[DrugProtocol]:
    """
    Get a drug protocol by ID.

    Args:
        db: Database session
        protocol_id: Protocol ID

    Returns:
        DrugProtocol or None

    Example:
        >>> protocol = get_drug_protocol(db, 1)
    """
    return db.query(DrugProtocol).filter(
        DrugProtocol.id == protocol_id
    ).first()


def get_protocol_by_name(
    db: Session,
    drug_name: str
) -> Optional[DrugProtocol]:
    """
    Get drug protocol by drug name.

    Args:
        db: Database session
        drug_name: Name of the drug

    Returns:
        DrugProtocol or None

    Example:
        >>> methylene_blue = get_protocol_by_name(db, "Methylene Blue")
        >>> print(methylene_blue.dosage_min)
    """
    return db.query(DrugProtocol).filter(
        DrugProtocol.drug_name == drug_name
    ).first()


def get_all_protocols(db: Session) -> List[DrugProtocol]:
    """
    Get all drug protocols.

    Args:
        db: Database session

    Returns:
        List of all DrugProtocol objects

    Example:
        >>> protocols = get_all_protocols(db)
        >>> for p in protocols:
        ...     print(p.drug_name)
    """
    return db.query(DrugProtocol).order_by(DrugProtocol.drug_name).all()


def search_protocols(
    db: Session,
    search_term: str
) -> List[DrugProtocol]:
    """
    Search drug protocols by name.

    Args:
        db: Database session
        search_term: Search term (partial match)

    Returns:
        List of matching DrugProtocol objects

    Example:
        >>> results = search_protocols(db, "blue")
        >>> # Returns protocols with "blue" in name
    """
    return db.query(DrugProtocol).filter(
        DrugProtocol.drug_name.ilike(f"%{search_term}%")
    ).all()


def update_drug_protocol(
    db: Session,
    protocol_id: int,
    protocol_update: DrugProtocolUpdate
) -> Optional[DrugProtocol]:
    """
    Update an existing drug protocol.

    Args:
        db: Database session
        protocol_id: Protocol ID
        protocol_update: Update schema

    Returns:
        Updated DrugProtocol or None

    Example:
        >>> update = DrugProtocolUpdate(
        ...     dosage_max=6.0,
        ...     notes="Updated maximum dosage"
        ... )
        >>> updated = update_drug_protocol(db, 1, update)
    """
    db_protocol = get_drug_protocol(db, protocol_id)
    if not db_protocol:
        return None

    update_data = protocol_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_protocol, field, value)

    db.commit()
    db.refresh(db_protocol)
    return db_protocol


def delete_drug_protocol(db: Session, protocol_id: int) -> bool:
    """
    Delete a drug protocol.

    Args:
        db: Database session
        protocol_id: Protocol ID

    Returns:
        True if deleted, False if not found

    Example:
        >>> deleted = delete_drug_protocol(db, 1)
    """
    db_protocol = get_drug_protocol(db, protocol_id)
    if not db_protocol:
        return False

    db.delete(db_protocol)
    db.commit()
    return True


def count_protocols(db: Session) -> int:
    """
    Count total drug protocols.

    Args:
        db: Database session

    Returns:
        Number of protocols

    Example:
        >>> total = count_protocols(db)
    """
    return db.query(DrugProtocol).count()
