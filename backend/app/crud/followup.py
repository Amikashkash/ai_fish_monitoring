"""
Filename: followup.py
Purpose: CRUD operations for follow-up assessment records
Author: Fish Monitoring System
Created: 2026-02-15

This module provides database operations for 5-day follow-up assessments.

Dependencies:
    - sqlalchemy.orm: Database session
    - app.models.followup: FollowupAssessment model
    - app.schemas.followup: Followup schemas

Example:
    >>> from app.crud import followup
    >>> new_followup = followup.create_followup(db, followup_data)
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.models.followup import FollowupAssessment
from app.schemas.followup import FollowupCreate, FollowupUpdate


def create_followup(
    db: Session,
    followup: FollowupCreate
) -> FollowupAssessment:
    """
    Create a new follow-up assessment.

    Args:
        db: Database session
        followup: Followup creation schema

    Returns:
        Created FollowupAssessment object

    Example:
        >>> followup_data = FollowupCreate(
        ...     treatment_id=1,
        ...     stability_score=5,
        ...     symptoms_returned=False,
        ...     survival_count=48,
        ...     success_rate=96.0
        ... )
        >>> followup = create_followup(db, followup_data)
    """
    db_followup = FollowupAssessment(**followup.model_dump())
    db.add(db_followup)
    db.commit()
    db.refresh(db_followup)
    return db_followup


def get_followup(
    db: Session,
    followup_id: int
) -> Optional[FollowupAssessment]:
    """
    Get a follow-up assessment by ID.

    Args:
        db: Database session
        followup_id: Followup ID

    Returns:
        FollowupAssessment or None

    Example:
        >>> followup = get_followup(db, 1)
    """
    return db.query(FollowupAssessment).filter(
        FollowupAssessment.id == followup_id
    ).first()


def get_followup_by_treatment(
    db: Session,
    treatment_id: int
) -> Optional[FollowupAssessment]:
    """
    Get follow-up assessment for a specific treatment.

    Typically there's only one follow-up per treatment.

    Args:
        db: Database session
        treatment_id: Treatment ID

    Returns:
        FollowupAssessment or None

    Example:
        >>> followup = get_followup_by_treatment(db, 1)
        >>> if followup:
        ...     print(f"Success rate: {followup.success_rate}%")
    """
    return db.query(FollowupAssessment).filter(
        FollowupAssessment.treatment_id == treatment_id
    ).first()


def get_followups(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> List[FollowupAssessment]:
    """
    Get list of follow-up assessments.

    Args:
        db: Database session
        skip: Records to skip
        limit: Maximum records

    Returns:
        List of FollowupAssessment objects

    Example:
        >>> followups = get_followups(db, skip=0, limit=20)
    """
    return db.query(FollowupAssessment).offset(skip).limit(limit).all()


def get_successful_followups(
    db: Session,
    threshold: float = 80.0
) -> List[FollowupAssessment]:
    """
    Get follow-ups with success rate above threshold.

    Args:
        db: Database session
        threshold: Minimum success rate percentage (default 80%)

    Returns:
        List of successful FollowupAssessment objects

    Example:
        >>> successful = get_successful_followups(db, threshold=90.0)
    """
    return db.query(FollowupAssessment).filter(
        FollowupAssessment.success_rate >= threshold
    ).all()


def get_followups_with_symptoms_returned(
    db: Session
) -> List[FollowupAssessment]:
    """
    Get follow-ups where symptoms returned after treatment.

    Args:
        db: Database session

    Returns:
        List of FollowupAssessment objects with returned symptoms

    Example:
        >>> problematic = get_followups_with_symptoms_returned(db)
    """
    return db.query(FollowupAssessment).filter(
        FollowupAssessment.symptoms_returned == True
    ).all()


def update_followup(
    db: Session,
    followup_id: int,
    followup_update: FollowupUpdate
) -> Optional[FollowupAssessment]:
    """
    Update an existing follow-up assessment.

    Args:
        db: Database session
        followup_id: Followup ID
        followup_update: Update schema

    Returns:
        Updated FollowupAssessment or None

    Example:
        >>> update = FollowupUpdate(
        ...     ai_learning_notes="Protocol added to knowledge base"
        ... )
        >>> updated = update_followup(db, 1, update)
    """
    db_followup = get_followup(db, followup_id)
    if not db_followup:
        return None

    update_data = followup_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_followup, field, value)

    db.commit()
    db.refresh(db_followup)
    return db_followup


def delete_followup(db: Session, followup_id: int) -> bool:
    """
    Delete a follow-up assessment.

    Args:
        db: Database session
        followup_id: Followup ID

    Returns:
        True if deleted, False if not found

    Example:
        >>> deleted = delete_followup(db, 1)
    """
    db_followup = get_followup(db, followup_id)
    if not db_followup:
        return False

    db.delete(db_followup)
    db.commit()
    return True


def calculate_average_success_rate(db: Session) -> Optional[float]:
    """
    Calculate average success rate across all follow-ups.

    Args:
        db: Database session

    Returns:
        Average success rate or None if no data

    Example:
        >>> avg = calculate_average_success_rate(db)
        >>> print(f"Average success rate: {avg}%")
    """
    from sqlalchemy import func

    result = db.query(
        func.avg(FollowupAssessment.success_rate)
    ).scalar()

    return float(result) if result else None


def count_followups(db: Session) -> int:
    """
    Count total follow-up assessments.

    Args:
        db: Database session

    Returns:
        Number of followups

    Example:
        >>> total = count_followups(db)
    """
    return db.query(FollowupAssessment).count()
