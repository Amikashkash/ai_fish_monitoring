"""
Filename: shipment.py
Purpose: CRUD operations for shipment database records
Author: Fish Monitoring System
Created: 2026-02-15

This module provides database operations for creating, reading,
updating, and deleting shipment records.

Dependencies:
    - sqlalchemy.orm: Database session
    - app.models.shipment: Shipment model
    - app.schemas.shipment: Shipment schemas

Example:
    >>> from app.crud import shipment
    >>> new_shipment = shipment.create_shipment(db, shipment_data)
    >>> shipment_list = shipment.get_shipments(db, skip=0, limit=10)
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.models.shipment import Shipment
from app.schemas.shipment import ShipmentCreate, ShipmentUpdate


def create_shipment(
    db: Session,
    shipment: ShipmentCreate
) -> Shipment:
    """
    Create a new shipment record.

    Args:
        db: Database session
        shipment: Shipment creation schema

    Returns:
        Created Shipment object

    Example:
        >>> shipment_data = ShipmentCreate(
        ...     scientific_name="Betta splendens",
        ...     common_name="Siamese Fighting Fish",
        ...     source="Thailand",
        ...     quantity=50,
        ...     aquarium_volume_liters=200
        ... )
        >>> new_shipment = create_shipment(db, shipment_data)
        >>> print(new_shipment.id)
        1
    """
    db_shipment = Shipment(**shipment.model_dump())
    db.add(db_shipment)
    db.commit()
    db.refresh(db_shipment)
    return db_shipment


def get_shipment(db: Session, shipment_id: int) -> Optional[Shipment]:
    """
    Get a shipment by ID.

    Args:
        db: Database session
        shipment_id: Shipment ID

    Returns:
        Shipment object or None if not found

    Example:
        >>> shipment = get_shipment(db, 1)
        >>> if shipment:
        ...     print(shipment.scientific_name)
    """
    return db.query(Shipment).filter(Shipment.id == shipment_id).first()


def get_shipments(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> List[Shipment]:
    """
    Get list of shipments with pagination.

    Args:
        db: Database session
        skip: Number of records to skip (offset)
        limit: Maximum number of records to return

    Returns:
        List of Shipment objects

    Example:
        >>> shipments = get_shipments(db, skip=0, limit=20)
        >>> print(f"Found {len(shipments)} shipments")
    """
    return db.query(Shipment).offset(skip).limit(limit).all()


def get_shipments_by_source(
    db: Session,
    source: str
) -> List[Shipment]:
    """
    Get all shipments from a specific source.

    Args:
        db: Database session
        source: Source country name

    Returns:
        List of Shipment objects from that source

    Example:
        >>> thailand_shipments = get_shipments_by_source(db, "Thailand")
        >>> print(f"Thailand shipments: {len(thailand_shipments)}")
    """
    return db.query(Shipment).filter(Shipment.source == source).all()


def get_shipments_by_species(
    db: Session,
    scientific_name: str
) -> List[Shipment]:
    """
    Get all shipments of a specific fish species.

    Args:
        db: Database session
        scientific_name: Scientific name of fish

    Returns:
        List of Shipment objects for that species

    Example:
        >>> bettas = get_shipments_by_species(db, "Betta splendens")
        >>> print(f"Betta shipments: {len(bettas)}")
    """
    return db.query(Shipment).filter(
        Shipment.scientific_name == scientific_name
    ).all()


def get_shipments_by_source_and_species(
    db: Session,
    source: str,
    scientific_name: str
) -> List[Shipment]:
    """
    Get shipments filtered by both source and species.

    Args:
        db: Database session
        source: Source country
        scientific_name: Fish species scientific name

    Returns:
        List of matching Shipment objects

    Example:
        >>> thai_bettas = get_shipments_by_source_and_species(
        ...     db, "Thailand", "Betta splendens"
        ... )
    """
    return db.query(Shipment).filter(
        Shipment.source == source,
        Shipment.scientific_name == scientific_name
    ).all()


def get_recent_shipments(
    db: Session,
    days: int = 30,
    limit: int = 50
) -> List[Shipment]:
    """
    Get recent shipments within specified days.

    Args:
        db: Database session
        days: Number of days to look back (default 30)
        limit: Maximum records to return

    Returns:
        List of recent Shipment objects

    Example:
        >>> recent = get_recent_shipments(db, days=7)
        >>> print(f"Shipments this week: {len(recent)}")
    """
    from datetime import timedelta
    cutoff_date = date.today() - timedelta(days=days)

    return db.query(Shipment).filter(
        Shipment.date >= cutoff_date
    ).order_by(Shipment.date.desc()).limit(limit).all()


def update_shipment(
    db: Session,
    shipment_id: int,
    shipment_update: ShipmentUpdate
) -> Optional[Shipment]:
    """
    Update an existing shipment.

    Args:
        db: Database session
        shipment_id: ID of shipment to update
        shipment_update: Update schema with new values

    Returns:
        Updated Shipment object or None if not found

    Example:
        >>> update = ShipmentUpdate(quantity=45)
        >>> updated = update_shipment(db, 1, update)
        >>> print(updated.quantity)
        45
    """
    db_shipment = get_shipment(db, shipment_id)
    if not db_shipment:
        return None

    # Update only provided fields
    update_data = shipment_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_shipment, field, value)

    db.commit()
    db.refresh(db_shipment)
    return db_shipment


def delete_shipment(db: Session, shipment_id: int) -> bool:
    """
    Delete a shipment record.

    Args:
        db: Database session
        shipment_id: ID of shipment to delete

    Returns:
        True if deleted, False if not found

    Example:
        >>> deleted = delete_shipment(db, 1)
        >>> if deleted:
        ...     print("Shipment deleted successfully")
    """
    db_shipment = get_shipment(db, shipment_id)
    if not db_shipment:
        return False

    db.delete(db_shipment)
    db.commit()
    return True


def count_shipments(db: Session) -> int:
    """
    Get total count of all shipments.

    Args:
        db: Database session

    Returns:
        Total number of shipments

    Example:
        >>> total = count_shipments(db)
        >>> print(f"Total shipments: {total}")
    """
    return db.query(Shipment).count()


def count_shipments_by_source(db: Session, source: str) -> int:
    """
    Count shipments from a specific source.

    Args:
        db: Database session
        source: Source country

    Returns:
        Number of shipments from that source

    Example:
        >>> count = count_shipments_by_source(db, "Thailand")
        >>> print(f"Thailand: {count} shipments")
    """
    return db.query(Shipment).filter(Shipment.source == source).count()
