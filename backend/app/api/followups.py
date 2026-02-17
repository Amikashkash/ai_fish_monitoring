"""Follow-up assessment API endpoints using Supabase REST API."""

from fastapi import APIRouter, Depends, HTTPException
from supabase import Client

from app.config.supabase_client import get_supabase
from app.schemas.followup import FollowupCreate, FollowupResponse

router = APIRouter(prefix="/api/followups", tags=["followups"])


@router.post("/", response_model=FollowupResponse, status_code=201)
async def create_followup(
    followup: FollowupCreate,
    supabase: Client = Depends(get_supabase)
):
    """Create a 5-day follow-up assessment."""
    try:
        data = {
            "treatment_id": followup.treatment_id,
            "followup_date": followup.followup_date.isoformat(),
            "symptoms_returned": followup.symptoms_returned,
        }
        if followup.stability_score is not None:
            data["stability_score"] = followup.stability_score
        if followup.returned_symptoms:
            data["returned_symptoms"] = followup.returned_symptoms
        if followup.survival_count is not None:
            data["survival_count"] = followup.survival_count
        if followup.success_rate is not None:
            data["success_rate"] = float(followup.success_rate)
        if followup.recommendation:
            data["recommendation"] = followup.recommendation
        if followup.ai_learning_notes:
            data["ai_learning_notes"] = followup.ai_learning_notes

        response = supabase.table("followups").insert(data).execute()
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create follow-up")
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create follow-up: {str(e)}")


@router.get("/treatment/{treatment_id}", response_model=FollowupResponse)
async def get_treatment_followup(
    treatment_id: int,
    supabase: Client = Depends(get_supabase)
):
    """Get follow-up assessment for a treatment."""
    try:
        response = (
            supabase.table("followups")
            .select("*")
            .eq("treatment_id", treatment_id)
            .execute()
        )
        if not response.data:
            raise HTTPException(status_code=404, detail="Follow-up not found")
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch follow-up: {str(e)}")
