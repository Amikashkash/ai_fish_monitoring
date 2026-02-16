"""
Filename: dependencies.py
Purpose: Reusable FastAPI dependencies
Author: Fish Monitoring System
Created: 2026-02-15

This module provides dependency injection functions for FastAPI routes.
Common dependencies include database sessions, authentication, etc.

Example:
    >>> from app.api.dependencies import get_db
    >>> @router.get("/items")
    >>> def list_items(db: Session = Depends(get_db)):
    ...     return db.query(Item).all()
"""

from typing import Generator
from sqlalchemy.orm import Session

from app.config.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    Dependency that provides database session to route handlers.

    Creates a new session for each request and ensures it is closed
    after the request completes, even if an error occurs.

    Yields:
        Database session

    Example:
        >>> @router.post("/shipments")
        >>> def create_shipment(
        ...     shipment: ShipmentCreate,
        ...     db: Session = Depends(get_db)
        ... ):
        ...     return crud.create_shipment(db, shipment)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
