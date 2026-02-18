"""Treatment API endpoints using Supabase REST API."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from supabase import Client
from datetime import date

from app.config.supabase_client import get_supabase
from app.schemas.treatment import TreatmentCreate, TreatmentResponse, TreatmentDrugCreate, TreatmentUpdate

router = APIRouter(prefix="/api/treatments", tags=["treatments"])


@router.get("/", response_model=List[TreatmentResponse])
async def list_treatments(
    active_only: bool = False,
    supabase: Client = Depends(get_supabase)
):
    """List all treatments or only active ones, including their drugs."""
    try:
        query = supabase.table("treatments").select("*, treatment_drugs(*)")
        if active_only:
            query = query.eq("status", "active")
        response = query.order("created_at", desc=True).execute()
        # Rename treatment_drugs → drugs to match TreatmentResponse schema
        treatments = []
        for t in response.data:
            t["drugs"] = t.pop("treatment_drugs", [])
            treatments.append(t)
        return treatments
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch treatments: {str(e)}")


@router.get("/{treatment_id}", response_model=TreatmentResponse)
async def get_treatment(
    treatment_id: int,
    supabase: Client = Depends(get_supabase)
):
    """Retrieve a treatment by ID."""
    try:
        response = supabase.table("treatments").select("*").eq("id", treatment_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Treatment not found")
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch treatment: {str(e)}")


@router.post("/", response_model=TreatmentResponse, status_code=201)
async def create_treatment(
    treatment: TreatmentCreate,
    supabase: Client = Depends(get_supabase)
):
    """Create a new treatment protocol for a shipment."""
    try:
        treatment_data = {
            "shipment_id": treatment.shipment_id,
            "start_date": treatment.start_date.isoformat(),
            "status": treatment.status,
        }
        if treatment.end_date:
            treatment_data["end_date"] = treatment.end_date.isoformat()

        response = supabase.table("treatments").insert(treatment_data).execute()
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create treatment")

        created = response.data[0]

        # Insert treatment drugs if provided
        if treatment.drugs:
            drugs_data = [
                {
                    "treatment_id": created["id"],
                    "drug_protocol_id": d.drug_protocol_id,
                    "actual_dosage": float(d.actual_dosage) if d.actual_dosage else None,
                    "actual_frequency": d.actual_frequency,
                    "notes": d.notes,
                }
                for d in treatment.drugs
            ]
            supabase.table("treatment_drugs").insert(drugs_data).execute()

        return created
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create treatment: {str(e)}")


@router.patch("/{treatment_id}", response_model=TreatmentResponse)
async def update_treatment(
    treatment_id: int,
    update: TreatmentUpdate,
    supabase: Client = Depends(get_supabase)
):
    """Update treatment fields (start_date, end_date, status)."""
    try:
        patch = {k: v.isoformat() if hasattr(v, "isoformat") else v
                 for k, v in update.model_dump(exclude_none=True).items()}
        if not patch:
            raise HTTPException(status_code=400, detail="No fields to update")
        response = supabase.table("treatments").update(patch).eq("id", treatment_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Treatment not found")
        result = response.data[0]
        result["drugs"] = []
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update treatment: {str(e)}")


@router.post("/{treatment_id}/drugs", status_code=201)
async def add_treatment_drug(
    treatment_id: int,
    drug: TreatmentDrugCreate,
    supabase: Client = Depends(get_supabase)
):
    """Add a drug protocol to an existing treatment."""
    try:
        data = {
            "treatment_id": treatment_id,
            "drug_protocol_id": drug.drug_protocol_id,
            "actual_dosage": float(drug.actual_dosage) if drug.actual_dosage else None,
            "actual_frequency": drug.actual_frequency,
            "notes": drug.notes,
        }
        response = supabase.table("treatment_drugs").insert(data).execute()
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to add drug")
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add drug: {str(e)}")


@router.delete("/{treatment_id}/drugs/{drug_id}", status_code=204)
async def remove_treatment_drug(
    treatment_id: int,
    drug_id: int,
    supabase: Client = Depends(get_supabase)
):
    """Remove a drug from a treatment."""
    try:
        supabase.table("treatment_drugs").delete().eq("id", drug_id).eq("treatment_id", treatment_id).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove drug: {str(e)}")


@router.post("/{treatment_id}/complete", response_model=TreatmentResponse)
async def complete_treatment(
    treatment_id: int,
    supabase: Client = Depends(get_supabase)
):
    """Mark a treatment as completed."""
    try:
        response = supabase.table("treatments").update({
            "status": "completed",
            "end_date": date.today().isoformat()
        }).eq("id", treatment_id).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Treatment not found")
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to complete treatment: {str(e)}")
