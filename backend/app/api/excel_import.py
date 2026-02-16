"""API endpoints for Excel file import and AI extraction."""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from supabase import Client
from datetime import datetime as DateTime
from typing import Optional

from app.config.supabase_client import get_supabase
from app.schemas.excel_import import (
    ExcelImportResponse,
    ExcelExtractionResult,
    ExcelExtractionValidation
)
from app.ai.excel_extractor import (
    extract_shipment_data_from_excel,
    validate_extracted_data
)

router = APIRouter(prefix="/api/excel-import", tags=["excel-import"])


@router.post("/extract", response_model=ExcelImportResponse)
async def extract_shipment_from_excel(
    file: UploadFile = File(..., description="Excel file (proforma or invoice)"),
    sheet_name: Optional[str] = None
):
    """
    Upload an Excel file and extract shipment data using AI.

    This endpoint accepts a proforma invoice or commercial invoice in Excel format
    and uses Claude AI to intelligently extract fish shipment information.

    Args:
        file: Excel file (.xlsx, .xls)
        sheet_name: Optional specific sheet name to analyze

    Returns:
        Extracted shipment data with validation results
    """
    # Validate file type
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    if not file.filename.lower().endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload an Excel file (.xlsx or .xls)"
        )

    try:
        # Extract data using AI
        extracted_data = await extract_shipment_data_from_excel(file, sheet_name)

        # Check if extraction failed
        if "error" in extracted_data:
            return ExcelImportResponse(
                success=False,
                data=None,
                validation=None,
                error=extracted_data["error"]
            )

        # Validate extracted data
        validation = validate_extracted_data(extracted_data)

        # Convert to response model
        extraction_result = ExcelExtractionResult(**extracted_data)
        validation_result = ExcelExtractionValidation(**validation)

        return ExcelImportResponse(
            success=True,
            data=extraction_result,
            validation=validation_result,
            error=None
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process Excel file: {str(e)}"
        )


@router.post("/extract-and-create-shipment")
async def extract_and_create_shipment(
    file: UploadFile = File(...),
    auto_create: bool = False,
    supabase: Client = Depends(get_supabase)
):
    """
    Extract data from Excel and optionally create a shipment record.

    If auto_create is True, will automatically create the shipment in the database.
    Otherwise, returns extracted data for user review.

    Args:
        file: Excel file
        auto_create: Whether to automatically create shipment
        supabase: Supabase client

    Returns:
        Extracted data and shipment ID if created
    """
    # First, extract the data
    extraction_response = await extract_shipment_from_excel(file)

    if not extraction_response.success or not extraction_response.data:
        raise HTTPException(status_code=400, detail=extraction_response.error or "Extraction failed")

    extracted_data = extraction_response.data
    validation = extraction_response.validation

    # Check if data is valid
    if validation and not validation.is_valid:
        return {
            "success": False,
            "extracted_data": extracted_data.model_dump(),
            "validation": validation.model_dump(),
            "message": "Extracted data has validation errors. Please review and correct.",
            "shipment_id": None
        }

    # If auto_create is True and data is valid, create shipment
    if auto_create:
        try:
            # Prepare shipment data
            shipment_data = {
                "source": extracted_data.source_country or "Unknown",
                "date": extracted_data.shipment_date.isoformat() if extracted_data.shipment_date else DateTime.now().date().isoformat(),
                "expected_arrival": extracted_data.expected_arrival.isoformat() if extracted_data.expected_arrival else None,
                "boxes": extracted_data.total_boxes or 0,
                "supplier_name": extracted_data.supplier_name or "Unknown",
                "invoice_number": extracted_data.invoice_number,
                "notes": extracted_data.additional_notes or "",
                "created_at": DateTime.now().isoformat()
            }

            # For now, we'll use the first species for the main shipment scientific name
            # In the future, you might want to handle multiple species differently
            if extracted_data.fish_species:
                first_species = extracted_data.fish_species[0]
                shipment_data["scientific_name"] = first_species.scientific_name or "Unknown"
                shipment_data["fish_count"] = sum(s.quantity for s in extracted_data.fish_species)

                # Store all species in notes for now
                species_list = "\n".join([
                    f"- {s.scientific_name or 'Unknown'}: {s.quantity} pcs" +
                    (f" ({s.size})" if s.size else "") +
                    (f" @ ${s.price_per_unit}" if s.price_per_unit else "")
                    for s in extracted_data.fish_species
                ])
                shipment_data["notes"] = f"Imported from Excel:\n{species_list}\n\n{shipment_data['notes']}"

            # Create shipment in Supabase
            result = supabase.table("shipments").insert(shipment_data).execute()

            if result.data:
                shipment_id = result.data[0]["id"]
                return {
                    "success": True,
                    "extracted_data": extracted_data.model_dump(),
                    "validation": validation.model_dump() if validation else None,
                    "message": f"Shipment created successfully with {len(extracted_data.fish_species)} species",
                    "shipment_id": shipment_id,
                    "shipment": result.data[0]
                }
            else:
                raise Exception("Failed to create shipment - no data returned")

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create shipment: {str(e)}"
            )

    # If not auto-creating, just return the extracted data for review
    return {
        "success": True,
        "extracted_data": extracted_data.model_dump(),
        "validation": validation.model_dump() if validation else None,
        "message": "Data extracted successfully. Review and confirm to create shipment.",
        "shipment_id": None
    }


@router.get("/supported-formats")
async def get_supported_formats():
    """
    Get information about supported Excel file formats and expected structure.

    Returns:
        Information about supported formats and examples
    """
    return {
        "supported_extensions": [".xlsx", ".xls"],
        "expected_content": {
            "supplier_info": "Supplier name and source country",
            "shipment_dates": "Shipment date and expected arrival",
            "invoice_details": "Invoice or proforma number",
            "fish_species": [
                {
                    "scientific_name": "Latin name (e.g., Pterophyllum scalare)",
                    "common_name": "Common name (optional)",
                    "quantity": "Number of fish",
                    "size": "Size description (optional)",
                    "price": "Price information (optional)"
                }
            ]
        },
        "tips": [
            "The AI can handle various Excel formats and layouts",
            "Ensure scientific names are clearly labeled",
            "Include supplier information if possible",
            "Multiple sheets are supported - specify sheet_name if needed"
        ],
        "ai_powered": True,
        "confidence_levels": ["high", "medium", "low"]
    }
