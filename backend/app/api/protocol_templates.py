"""Protocol template API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from supabase import Client

from app.config.supabase_client import get_supabase
from app.schemas.protocol_template import (
    ProtocolTemplateCreate,
    ProtocolTemplateUpdate,
    ProtocolTemplateResponse,
    ProtocolTemplateDetailResponse,
    ProtocolTemplateWithDrugDetails,
    ProtocolTemplateUsageUpdate,
    ProtocolTemplateDrugCreate
)

router = APIRouter(prefix="/api/protocol-templates", tags=["protocol-templates"])


@router.get("/", response_model=List[ProtocolTemplateResponse])
async def list_protocol_templates(
    purpose: Optional[str] = Query(None, description="Filter by treatment purpose"),
    min_success_rate: Optional[float] = Query(None, description="Minimum success rate percentage"),
    supabase: Client = Depends(get_supabase)
):
    """Get all protocol templates with optional filtering."""
    try:
        query = supabase.table("protocol_templates").select("*")

        if purpose:
            query = query.ilike("purpose", f"%{purpose}%")

        if min_success_rate is not None:
            query = query.gte("success_rate", min_success_rate)

        query = query.order("success_rate", desc=True)

        response = query.execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch protocol templates: {str(e)}")


@router.get("/{template_id}", response_model=ProtocolTemplateDetailResponse)
async def get_protocol_template(
    template_id: int,
    supabase: Client = Depends(get_supabase)
):
    """Get a specific protocol template with all drug details."""
    try:
        # Get template
        template_response = supabase.table("protocol_templates").select("*").eq("id", template_id).execute()
        if not template_response.data:
            raise HTTPException(status_code=404, detail="Protocol template not found")

        template = template_response.data[0]

        # Get associated drugs
        drugs_response = supabase.table("protocol_template_drugs").select("*").eq("protocol_template_id", template_id).order("sequence_order").execute()

        template["drugs"] = drugs_response.data
        return template
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch protocol template: {str(e)}")


@router.get("/details/{template_id}")
async def get_protocol_template_with_full_details(
    template_id: int,
    supabase: Client = Depends(get_supabase)
):
    """Get protocol template with full drug information from the view."""
    try:
        # Use the view for complete information
        response = supabase.table("protocol_template_details").select("*").eq("template_id", template_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Protocol template not found")
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch protocol template details: {str(e)}")


@router.post("/", response_model=ProtocolTemplateResponse, status_code=201)
async def create_protocol_template(
    template: ProtocolTemplateCreate,
    supabase: Client = Depends(get_supabase)
):
    """Create a new protocol template with associated drugs."""
    try:
        # Create the protocol template
        template_data = template.model_dump(exclude={"drugs"})
        template_response = supabase.table("protocol_templates").insert(template_data).execute()

        if not template_response.data:
            raise HTTPException(status_code=500, detail="Failed to create protocol template")

        created_template = template_response.data[0]
        template_id = created_template["id"]

        # Add drugs to the protocol
        if template.drugs:
            drugs_data = []
            for drug in template.drugs:
                drug_dict = drug.model_dump()
                drug_dict["protocol_template_id"] = template_id
                drugs_data.append(drug_dict)

            supabase.table("protocol_template_drugs").insert(drugs_data).execute()

        return created_template
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create protocol template: {str(e)}")


@router.put("/{template_id}", response_model=ProtocolTemplateResponse)
async def update_protocol_template(
    template_id: int,
    template: ProtocolTemplateUpdate,
    supabase: Client = Depends(get_supabase)
):
    """Update a protocol template."""
    try:
        # Check if template exists
        existing = supabase.table("protocol_templates").select("*").eq("id", template_id).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="Protocol template not found")

        # Update template fields
        update_data = template.model_dump(exclude={"drugs"}, exclude_unset=True)
        if update_data:
            template_response = supabase.table("protocol_templates").update(update_data).eq("id", template_id).execute()
        else:
            template_response = existing

        # Update drugs if provided
        if template.drugs is not None:
            # Delete existing drugs
            supabase.table("protocol_template_drugs").delete().eq("protocol_template_id", template_id).execute()

            # Add new drugs
            if template.drugs:
                drugs_data = []
                for drug in template.drugs:
                    drug_dict = drug.model_dump()
                    drug_dict["protocol_template_id"] = template_id
                    drugs_data.append(drug_dict)

                supabase.table("protocol_template_drugs").insert(drugs_data).execute()

        return template_response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update protocol template: {str(e)}")


@router.delete("/{template_id}", status_code=204)
async def delete_protocol_template(
    template_id: int,
    supabase: Client = Depends(get_supabase)
):
    """Delete a protocol template."""
    try:
        # Check if template exists
        existing = supabase.table("protocol_templates").select("*").eq("id", template_id).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="Protocol template not found")

        # Delete template (drugs will be cascade deleted)
        supabase.table("protocol_templates").delete().eq("id", template_id).execute()

        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete protocol template: {str(e)}")


@router.post("/{template_id}/usage", response_model=ProtocolTemplateResponse)
async def update_protocol_usage(
    template_id: int,
    usage: ProtocolTemplateUsageUpdate,
    supabase: Client = Depends(get_supabase)
):
    """Update usage statistics for a protocol template after it's been used."""
    try:
        # Get current template
        template_response = supabase.table("protocol_templates").select("*").eq("id", template_id).execute()
        if not template_response.data:
            raise HTTPException(status_code=404, detail="Protocol template not found")

        template = template_response.data[0]

        # Increment usage counters
        new_times_used = template["times_used"] + 1
        new_successful = template["successful_outcomes"] + (1 if usage.was_successful else 0)

        # Update template
        update_response = supabase.table("protocol_templates").update({
            "times_used": new_times_used,
            "successful_outcomes": new_successful
        }).eq("id", template_id).execute()

        return update_response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update protocol usage: {str(e)}")


@router.get("/recommend/by-purpose")
async def recommend_protocols_by_purpose(
    purpose: str = Query(..., description="Treatment purpose to find protocols for"),
    min_success_rate: Optional[float] = Query(None, description="Minimum success rate percentage"),
    limit: int = Query(5, description="Maximum number of recommendations"),
    supabase: Client = Depends(get_supabase)
):
    """Get recommended protocol templates for a specific purpose, ordered by success rate."""
    try:
        query = supabase.table("protocol_template_details").select("*").ilike("purpose", f"%{purpose}%")

        if min_success_rate is not None:
            query = query.gte("success_rate", min_success_rate)

        response = query.order("success_rate", desc=True).limit(limit).execute()

        return {
            "purpose": purpose,
            "recommendations": response.data,
            "count": len(response.data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get protocol recommendations: {str(e)}")
