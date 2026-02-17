"""Drug protocol API endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from supabase import Client

from app.config.supabase_client import get_supabase
from app.schemas.drug_protocol import DrugProtocolCreate, DrugProtocolUpdate, DrugProtocolResponse

router = APIRouter(prefix="/api/protocols", tags=["protocols"])


@router.get("/", response_model=List[DrugProtocolResponse])
async def list_protocols(supabase: Client = Depends(get_supabase)):
    """Get all drug protocols."""
    try:
        response = supabase.table("drug_protocols").select("*").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch protocols: {str(e)}")


@router.get("/{protocol_id}", response_model=DrugProtocolResponse)
async def get_protocol(
    protocol_id: int,
    supabase: Client = Depends(get_supabase)
):
    """Get a specific drug protocol."""
    try:
        response = supabase.table("drug_protocols").select("*").eq("id", protocol_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Protocol not found")
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch protocol: {str(e)}")


@router.post("/", response_model=DrugProtocolResponse, status_code=201)
async def create_protocol(
    protocol: DrugProtocolCreate,
    supabase: Client = Depends(get_supabase)
):
    """Create a new drug protocol."""
    try:
        response = supabase.table("drug_protocols").insert(protocol.model_dump(mode="json")).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create protocol: {str(e)}")


@router.put("/{protocol_id}", response_model=DrugProtocolResponse)
async def update_protocol(
    protocol_id: int,
    protocol: DrugProtocolUpdate,
    supabase: Client = Depends(get_supabase)
):
    """Update an existing drug protocol."""
    try:
        data = {k: v for k, v in protocol.model_dump(mode="json").items() if v is not None}
        if not data:
            raise HTTPException(status_code=400, detail="No fields to update")
        response = supabase.table("drug_protocols").update(data).eq("id", protocol_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Protocol not found")
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update protocol: {str(e)}")


@router.delete("/{protocol_id}", status_code=204)
async def delete_protocol(
    protocol_id: int,
    supabase: Client = Depends(get_supabase)
):
    """Delete a drug protocol."""
    try:
        response = supabase.table("drug_protocols").delete().eq("id", protocol_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Protocol not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete protocol: {str(e)}")
