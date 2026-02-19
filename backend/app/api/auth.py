"""Auth endpoint — single-admin password login returning a JWT."""

import secrets
from datetime import datetime, timezone, timedelta

import jwt
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.config.settings import get_settings

router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginRequest(BaseModel):
    password: str


class TokenResponse(BaseModel):
    token: str


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest):
    """Verify admin password and return a 30-day JWT."""
    settings = get_settings()

    # Timing-safe comparison
    if not secrets.compare_digest(body.password, settings.ADMIN_PASSWORD):
        raise HTTPException(status_code=401, detail="Wrong password")

    payload = {
        "role": "admin",
        "exp": datetime.now(timezone.utc) + timedelta(days=30),
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")
    return {"token": token}
