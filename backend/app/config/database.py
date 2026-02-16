"""
Filename: database.py
Purpose: Database connection configuration and session management
Author: Fish Monitoring System
Created: 2026-02-15

This module provides database connection setup for Supabase PostgreSQL
and session management for SQLAlchemy ORM operations.

Dependencies:
    - sqlalchemy: ORM and database toolkit
    - app.config.settings: Application settings

Example:
    >>> from app.config.database import get_db
    >>> db = next(get_db())
    >>> # Use db session for queries
    >>> db.close()
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from urllib.parse import quote_plus

from app.config.settings import get_settings

# Get application settings
settings = get_settings()

# Construct PostgreSQL database URL for Supabase
# Format: postgresql://postgres.[project-ref]:[password]@[pooler-host]:[port]/postgres
# Note: Supabase provides connection details in project settings
project_ref = settings.SUPABASE_URL.split('//')[1].split('.')[0]
# URL-encode password to handle special characters like @
encoded_password = quote_plus(settings.SUPABASE_DB_PASSWORD)
DATABASE_URL = (
    f"postgresql://postgres.{project_ref}:{encoded_password}@"
    f"db.blgqdtvwizxdiyeiciwf.supabase.co:5432/postgres"
)

# Create SQLAlchemy engine
# pool_pre_ping=True ensures connection health checks
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)

# Create session factory
# autocommit=False: Transactions must be explicitly committed
# autoflush=False: Changes aren't automatically flushed to DB
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for ORM models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.

    Yields database session and ensures it's closed after use.
    This is used as a FastAPI dependency for automatic session management.

    Yields:
        SQLAlchemy Session object

    Example:
        In FastAPI route:
        >>> @router.get("/shipments")
        >>> async def get_shipments(db: Session = Depends(get_db)):
        >>>     shipments = db.query(Shipment).all()
        >>>     return shipments
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database tables.

    Creates all tables defined in models if they don't exist.
    Note: In production, use Alembic migrations instead.

    Example:
        >>> from app.config.database import init_db
        >>> init_db()  # Creates all tables
    """
    # Import all models to ensure they're registered with Base
    from app.models import (
        shipment,
        treatment,
        observation,
        followup,
        drug_protocol,
        ai_knowledge
    )

    Base.metadata.create_all(bind=engine)
