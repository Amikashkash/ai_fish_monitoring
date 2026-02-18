"""Daily observation API endpoints using Supabase REST API."""

from typing import List
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from supabase import Client

from app.config.supabase_client import get_supabase
from app.schemas.observation import ObservationCreate, ObservationResponse

router = APIRouter(prefix="/api/observations", tags=["observations"])


@router.post("/", response_model=ObservationResponse, status_code=201)
async def create_observation(
    observation: ObservationCreate,
    supabase: Client = Depends(get_supabase)
):
    """Record a daily observation for a treatment."""
    try:
        data = {
            "treatment_id": observation.treatment_id,
            "observation_date": observation.observation_date.isoformat(),
            "symptoms_lethargy": observation.symptoms_lethargy,
            "symptoms_loss_of_appetite": observation.symptoms_loss_of_appetite,
            "symptoms_spots": observation.symptoms_spots,
            "symptoms_fin_damage": observation.symptoms_fin_damage,
            "symptoms_breathing_issues": observation.symptoms_breathing_issues,
            "treatments_completed": observation.treatments_completed,
        }
        if observation.overall_condition_score is not None:
            data["overall_condition_score"] = observation.overall_condition_score
        if observation.symptoms_other:
            data["symptoms_other"] = observation.symptoms_other
        if observation.dead_fish_count is not None:
            data["dead_fish_count"] = observation.dead_fish_count
        if observation.condition_trend:
            data["condition_trend"] = observation.condition_trend
        if observation.notes:
            data["notes"] = observation.notes

        try:
            response = supabase.table("daily_observations").insert(data).execute()
        except Exception as first_err:
            if "PGRST204" in str(first_err):
                # New columns not yet in DB — strip them and retry
                for col in ("dead_fish_count", "condition_trend"):
                    data.pop(col, None)
                response = supabase.table("daily_observations").insert(data).execute()
            else:
                raise first_err

        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create observation")
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create observation: {str(e)}")


@router.get("/today", response_model=List[ObservationResponse])
async def get_today_observations(supabase: Client = Depends(get_supabase)):
    """Get all observations recorded today."""
    try:
        today = date.today().isoformat()
        response = (
            supabase.table("daily_observations")
            .select("*")
            .eq("observation_date", today)
            .execute()
        )
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch today's observations: {str(e)}")


@router.get("/treatment/{treatment_id}", response_model=List[ObservationResponse])
async def get_treatment_observations(
    treatment_id: int,
    supabase: Client = Depends(get_supabase)
):
    """Get all observations for a specific treatment."""
    try:
        response = (
            supabase.table("daily_observations")
            .select("*")
            .eq("treatment_id", treatment_id)
            .order("observation_date")
            .execute()
        )
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch observations: {str(e)}")
