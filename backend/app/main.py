"""
Filename: main.py
Purpose: FastAPI application entry point
Author: Fish Monitoring System
Created: 2026-02-15

Main application file that initializes FastAPI, configures CORS,
registers all API routes, and sets up middleware.

Run with: uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import get_settings
from app.config.database import Base, engine
from app.api import (
    shipments,
    treatments,
    observations,
    followups,
    protocols,
    recommendations,
    suppliers,
    tasks
)

# Initialize settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="Fish Monitoring System API",
    description="AI-powered fish acclimation tracking and treatment recommendations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
origins = settings.CORS_ORIGINS.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(shipments.router)
app.include_router(treatments.router)
app.include_router(observations.router)
app.include_router(followups.router)
app.include_router(protocols.router)
app.include_router(recommendations.router)
app.include_router(suppliers.router)
app.include_router(tasks.router)


@app.get("/")
async def root():
    """Root endpoint - health check."""
    return {
        "status": "ok",
        "message": "Fish Monitoring System API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "database": "connected"
    }


# Create database tables on startup (for development)
# In production, use Supabase migrations instead
@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    # Note: Comment this out when using Supabase
    # Base.metadata.create_all(bind=engine)
    print("Fish Monitoring System API started")
    print(f"API docs available at http://localhost:8000/docs")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    print("Fish Monitoring System API shutting down")
