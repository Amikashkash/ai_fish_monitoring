"""Daily tasks API endpoint for n8n automation."""

from typing import List, Dict
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.crud import treatment as treatment_crud
from app.services.treatment_scheduler import get_daily_treatment_tasks

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("/daily")
async def get_daily_tasks(db: Session = Depends(get_db)) -> Dict:
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
    active_treatments = treatment_crud.get_active_treatments(db)
    
    tasks = []
    for treatment in active_treatments:
        shipment = treatment.shipment
        tasks.append({
            "treatment_id": treatment.id,
            "fish_species": shipment.scientific_name,
            "common_name": shipment.common_name,
            "source": shipment.source,
            "quantity": shipment.quantity,
            "start_date": str(treatment.start_date),
            "drugs_required": [
                {
                    "name": td.drug_protocol.drug_name if hasattr(td, 'drug_protocol') else "Unknown",
                    "dosage": str(td.actual_dosage),
                    "frequency": td.actual_frequency
                }
                for td in treatment.treatment_drugs
            ] if hasattr(treatment, 'treatment_drugs') else []
        })
    
    return {
        "date": str(datetime.now().date()),
        "total_active_treatments": len(tasks),
        "tasks": tasks
    }


from datetime import datetime
