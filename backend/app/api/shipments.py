"""Shipment API endpoints using Supabase REST API."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from supabase import Client

from app.config.supabase_client import get_supabase
from app.schemas.shipment import ShipmentCreate, ShipmentResponse, ShipmentList

router = APIRouter(prefix="/api/shipments", tags=["shipments"])


@router.post("/", response_model=ShipmentResponse, status_code=201)
async def create_shipment(
    shipment: ShipmentCreate,
    supabase: Client = Depends(get_supabase)
):
    """Create a new fish shipment record."""
    try:
        data = {
            "scientific_name": shipment.scientific_name,
            # common_name is NOT NULL in DB; fall back to scientific_name
            "common_name": shipment.common_name or shipment.scientific_name,
            "source": shipment.source,
            "quantity": shipment.quantity,
            "date": shipment.date.isoformat(),
        }
        # aquarium_volume_liters is NOT NULL in DB; use 1 as placeholder until assigned
        data["aquarium_volume_liters"] = shipment.aquarium_volume_liters or 1
        if shipment.aquarium_number:
            data["aquarium_number"] = shipment.aquarium_number
        if shipment.fish_size:
            data["fish_size"] = shipment.fish_size
        if shipment.price_per_fish is not None:
            data["price_per_fish"] = float(shipment.price_per_fish)
        if shipment.total_price is not None:
            data["total_price"] = float(shipment.total_price)
        if shipment.notes:
            data["notes"] = shipment.notes
        if shipment.invoice_number:
            data["invoice_number"] = shipment.invoice_number
        if shipment.supplier_name:
            data["supplier_name"] = shipment.supplier_name

        try:
            response = supabase.table("shipments").insert(data).execute()
        except Exception as first_err:
            # PGRST204 = column not found (migration not yet run).
            # Retry with only the original columns that are guaranteed to exist.
            if "PGRST204" in str(first_err):
                for col in ("notes", "invoice_number", "supplier_name", "aquarium_number"):
                    data.pop(col, None)
                response = supabase.table("shipments").insert(data).execute()
            else:
                raise first_err

        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create shipment")
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create shipment: {str(e)}")


@router.delete("/{shipment_id}", status_code=204)
async def delete_shipment(
    shipment_id: int,
    supabase: Client = Depends(get_supabase)
):
    """Delete a shipment (e.g. DOA, shipping problem)."""
    try:
        response = supabase.table("shipments").delete().eq("id", shipment_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Shipment not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete shipment: {str(e)}")


@router.patch("/{shipment_id}", response_model=ShipmentResponse)
async def update_shipment(
    shipment_id: int,
    data: dict,
    supabase: Client = Depends(get_supabase)
):
    """Partially update a shipment (aquarium info, etc.)."""
    try:
        # Only allow safe fields to be updated
        allowed = {"aquarium_number", "aquarium_volume_liters", "common_name",
                   "fish_size", "notes", "invoice_number", "supplier_name", "invoice_id"}
        update_data = {k: v for k, v in data.items() if k in allowed}
        if not update_data:
            raise HTTPException(status_code=400, detail="No updatable fields provided")
        response = supabase.table("shipments").update(update_data).eq("id", shipment_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Shipment not found")
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update shipment: {str(e)}")


@router.get("/{shipment_id}", response_model=ShipmentResponse)
async def get_shipment(
    shipment_id: int,
    supabase: Client = Depends(get_supabase)
):
    """Retrieve a shipment by ID."""
    try:
        response = supabase.table("shipments").select("*").eq("id", shipment_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Shipment not found")
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch shipment: {str(e)}")


@router.get("/", response_model=ShipmentList)
async def list_shipments(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    source: Optional[str] = None,
    scientific_name: Optional[str] = None,
    supabase: Client = Depends(get_supabase)
):
    """List shipments with optional filtering and pagination."""
    try:
        query = supabase.table("shipments").select("*", count="exact")
        if source:
            query = query.ilike("source", f"%{source}%")
        if scientific_name:
            query = query.ilike("scientific_name", f"%{scientific_name}%")

        response = query.order("date", desc=True).range(skip, skip + limit - 1).execute()
        total = response.count if response.count is not None else len(response.data)

        return ShipmentList(
            total=total,
            page=skip // limit + 1,
            page_size=limit,
            shipments=response.data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch shipments: {str(e)}")
