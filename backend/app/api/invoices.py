"""Invoice API endpoints — shipment header with nested fish items."""

from fastapi import APIRouter, Depends, HTTPException
from supabase import Client

from app.config.supabase_client import get_supabase
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate, FishItemCreate

router = APIRouter(prefix="/api/invoices", tags=["invoices"])


@router.get("/")
async def list_invoices(supabase: Client = Depends(get_supabase)):
    """List all invoices with their nested fish items (shipments)."""
    try:
        response = (
            supabase.table("invoices")
            .select("*, shipments(*)")
            .order("date", desc=True)
            .execute()
        )
        return response.data or []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch invoices: {str(e)}")


@router.post("/", status_code=201)
async def create_invoice(
    invoice: InvoiceCreate,
    supabase: Client = Depends(get_supabase)
):
    """Create a new invoice (shipment header)."""
    try:
        data = {
            "date": invoice.date.isoformat(),
            "source": invoice.source,
        }
        if invoice.supplier_name:
            data["supplier_name"] = invoice.supplier_name
        if invoice.invoice_number:
            data["invoice_number"] = invoice.invoice_number
        if invoice.notes:
            data["notes"] = invoice.notes

        response = supabase.table("invoices").insert(data).execute()
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create invoice")
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create invoice: {str(e)}")


@router.patch("/{invoice_id}")
async def update_invoice(
    invoice_id: int,
    invoice: InvoiceUpdate,
    supabase: Client = Depends(get_supabase)
):
    """Update invoice header fields."""
    try:
        data = {}
        if invoice.date is not None:
            data["date"] = invoice.date.isoformat()
        if invoice.supplier_name is not None:
            data["supplier_name"] = invoice.supplier_name
        if invoice.invoice_number is not None:
            data["invoice_number"] = invoice.invoice_number
        if invoice.source is not None:
            data["source"] = invoice.source
        if invoice.notes is not None:
            data["notes"] = invoice.notes

        if not data:
            raise HTTPException(status_code=400, detail="No updatable fields provided")

        response = supabase.table("invoices").update(data).eq("id", invoice_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Invoice not found")
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update invoice: {str(e)}")


@router.delete("/{invoice_id}", status_code=204)
async def delete_invoice(
    invoice_id: int,
    supabase: Client = Depends(get_supabase)
):
    """Delete an invoice. Fish items become standalone (invoice_id set to NULL via FK ON DELETE SET NULL)."""
    try:
        response = supabase.table("invoices").delete().eq("id", invoice_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Invoice not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete invoice: {str(e)}")


@router.post("/{invoice_id}/fish", status_code=201)
async def add_fish_to_invoice(
    invoice_id: int,
    fish: FishItemCreate,
    supabase: Client = Depends(get_supabase)
):
    """Add a fish species (shipment row) to an existing invoice."""
    try:
        # Fetch invoice to verify existence and inherit source/date
        inv = supabase.table("invoices").select("*").eq("id", invoice_id).execute()
        if not inv.data:
            raise HTTPException(status_code=404, detail="Invoice not found")
        invoice = inv.data[0]

        data = {
            "invoice_id": invoice_id,
            "scientific_name": fish.scientific_name,
            "common_name": fish.common_name or fish.scientific_name,
            "quantity": fish.quantity,
            # Inherit source and date from invoice
            "source": invoice.get("source", ""),
            "date": invoice.get("date", ""),
            # aquarium_volume_liters is NOT NULL — default to 1 until assigned
            "aquarium_volume_liters": fish.aquarium_volume_liters or 1,
        }
        if fish.fish_size:
            data["fish_size"] = fish.fish_size
        if fish.aquarium_number:
            data["aquarium_number"] = fish.aquarium_number
        if fish.price_per_fish is not None:
            data["price_per_fish"] = float(fish.price_per_fish)
        if fish.notes:
            data["notes"] = fish.notes

        response = supabase.table("shipments").insert(data).execute()
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to add fish to invoice")
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add fish: {str(e)}")
