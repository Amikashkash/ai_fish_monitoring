"""Drug protocol API endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.schemas.drug_protocol import DrugProtocolCreate, DrugProtocolResponse
from app.crud import drug_protocol as protocol_crud

router = APIRouter(prefix="/api/protocols", tags=["protocols"])


@router.get("/", response_model=List[DrugProtocolResponse])
async def list_protocols(db: Session = Depends(get_db)):
    """Get all drug protocols."""
    protocols = protocol_crud.get_all_protocols(db)
    return protocols


@router.get("/{protocol_id}", response_model=DrugProtocolResponse)
async def get_protocol(
    protocol_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific drug protocol."""
    protocol = protocol_crud.get_drug_protocol(db, protocol_id)
    if not protocol:
        raise HTTPException(status_code=404, detail="Protocol not found")
    return protocol


@router.post("/", response_model=DrugProtocolResponse, status_code=201)
async def create_protocol(
    protocol: DrugProtocolCreate,
    db: Session = Depends(get_db)
):
    """Create a new drug protocol."""
    try:
        db_protocol = protocol_crud.create_drug_protocol(db=db, protocol=protocol)
        return db_protocol
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to create protocol")
