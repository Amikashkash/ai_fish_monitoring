"""
Filename: shipments.py
Purpose: Shipment API endpoints
Author: Fish Monitoring System
Created: 2026-02-15

Handles HTTP requests for creating and retrieving fish shipments.
Routes delegate business logic to services and CRUD operations.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.schemas.shipment import ShipmentCreate, ShipmentResponse, ShipmentList
from app.crud import shipment as shipment_crud
from app.services.density_calculator import calculate_density

router = APIRouter(prefix="/api/shipments", tags=["shipments"])


@router.post("/", response_model=ShipmentResponse, status_code=201)
async def create_shipment(
    shipment: ShipmentCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new fish shipment record.

    This endpoint:
    1. Validates input data
    2. Calculates density automatically
    3. Saves shipment to database
    4. Returns created shipment with ID

    Args:
        shipment: Shipment data (fish details, source, quantity, volume)
        db: Database session (injected)

    Returns:
        Created shipment with generated ID and calculated density

    Raises:
        HTTPException 400: If validation fails
        HTTPException 500: If database error occurs
    """
    try:
        db_shipment = shipment_crud.create_shipment(db=db, shipment=shipment)
        return db_shipment
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create shipment")


@router.get("/{shipment_id}", response_model=ShipmentResponse)
async def get_shipment(
    shipment_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve a shipment by ID.

    Args:
        shipment_id: Unique shipment identifier
        db: Database session (injected)

    Returns:
        Shipment details if found

    Raises:
        HTTPException 404: If shipment not found
    """
    shipment = shipment_crud.get_shipment(db, shipment_id)
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return shipment


@router.get("/", response_model=ShipmentList)
async def list_shipments(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    source: str = None,
    scientific_name: str = None,
    db: Session = Depends(get_db)
):
    """
    List shipments with optional filtering and pagination.

    Args:
        skip: Number of records to skip (pagination)
        limit: Maximum records to return (default 50, max 100)
        source: Filter by source country (optional)
        scientific_name: Filter by fish species (optional)
        db: Database session (injected)

    Returns:
        List of shipments with total count
    """
    if source and scientific_name:
        shipments = shipment_crud.get_shipments_by_source_and_species(
            db, source=source, scientific_name=scientific_name
        )
    elif source:
        shipments = shipment_crud.get_shipments_by_source(db, source=source)
    elif scientific_name:
        shipments = shipment_crud.get_shipments_by_species(db, scientific_name=scientific_name)
    else:
        shipments = shipment_crud.get_shipments(db, skip=skip, limit=limit)

    total = shipment_crud.count_shipments(db)
    
    return ShipmentList(
        shipments=shipments,
        total=total,
        skip=skip,
        limit=limit
    )
