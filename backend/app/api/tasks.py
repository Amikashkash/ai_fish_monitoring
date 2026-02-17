"""Daily tasks API endpoint for n8n automation using Supabase REST API."""

from datetime import datetime
from typing import Dict
from fastapi import APIRouter, Depends, HTTPException
from supabase import Client

from app.config.supabase_client import get_supabase

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("/daily")
async def get_daily_tasks(supabase: Client = Depends(get_supabase)) -> Dict:
    """
    Get today's tasks for n8n automation.

    Returns list of active treatments that need:
    - Daily observations
    - Drug administration
    - Monitoring

    Used by n8n to send daily WhatsApp reminders.

    Returns:
        Dictionary with active treatments and task details
    """
    try:
        response = (
            supabase.table("treatments")
            .select("*, shipments(*), treatment_drugs(*, drug_protocols(*))")
            .eq("status", "active")
            .execute()
        )

        tasks = []
        for treatment in (response.data or []):
            shipment = treatment.get("shipments") or {}
            drugs = treatment.get("treatment_drugs") or []

            tasks.append({
                "treatment_id": treatment["id"],
                "fish_species": shipment.get("scientific_name", ""),
                "common_name": shipment.get("common_name", ""),
                "source": shipment.get("source", ""),
                "quantity": shipment.get("quantity", 0),
                "start_date": str(treatment.get("start_date", "")),
                "drugs_required": [
                    {
                        "name": (d.get("drug_protocols") or {}).get("drug_name", "Unknown"),
                        "dosage": str(d.get("actual_dosage", "")),
                        "frequency": d.get("actual_frequency", "")
                    }
                    for d in drugs
                ]
            })

        return {
            "date": str(datetime.now().date()),
            "total_active_treatments": len(tasks),
            "tasks": tasks
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch daily tasks: {str(e)}")
