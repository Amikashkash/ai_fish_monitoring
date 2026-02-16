"""
Filename: treatment_scheduler.py
Purpose: Treatment scheduling and task management utilities
Author: Fish Monitoring System
Created: 2026-02-15

This module provides functions for scheduling treatments,
determining which treatments are active, and identifying
follow-up tasks.

Dependencies:
    - datetime: Date handling
    - app.utils.date_helpers: Date utilities
    - sqlalchemy.orm: Database session

Example:
    >>> from app.services.treatment_scheduler import get_treatments_ending_today
    >>> ending = get_treatments_ending_today(db)
"""

from datetime import date
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.treatment import Treatment
from app.utils.date_helpers import get_today, get_followup_date, add_days


def get_active_treatments(db: Session) -> List[Treatment]:
    """
    Get all currently active treatments.

    Args:
        db: Database session

    Returns:
        List of Treatment objects with status='active'

    Example:
        >>> treatments = get_active_treatments(db)
        >>> len(treatments)
        3
    """
    return db.query(Treatment).filter(
        Treatment.status == "active"
    ).all()


def get_treatments_ending_today(db: Session) -> List[Treatment]:
    """
    Get treatments scheduled to end today.

    Args:
        db: Database session

    Returns:
        List of Treatment objects ending today

    Example:
        >>> treatments = get_treatments_ending_today(db)
        >>> for t in treatments:
        ...     print(f"Treatment {t.id} ends today")
    """
    today = get_today()
    return db.query(Treatment).filter(
        Treatment.end_date == today,
        Treatment.status == "active"
    ).all()


def get_treatments_needing_followup(db: Session) -> List[Treatment]:
    """
    Get treatments that need 5-day follow-up today.

    Args:
        db: Database session

    Returns:
        List of Treatment objects needing follow-up assessment today

    Example:
        >>> treatments = get_treatments_needing_followup(db)
        >>> for t in treatments:
        ...     followup_date = get_followup_date(t.end_date)
        ...     print(f"Follow-up for treatment {t.id}")
    """
    today = get_today()
    followup_target_date = add_days(today, -5)  # Treatments that ended 5 days ago

    return db.query(Treatment).filter(
        Treatment.end_date == followup_target_date,
        Treatment.status == "completed"
    ).all()


def get_daily_treatment_tasks(db: Session) -> dict:
    """
    Get all treatment-related tasks for today.

    Returns dictionary with active treatments, ending treatments,
    and follow-ups needed.

    Args:
        db: Database session

    Returns:
        Dictionary with task lists

    Example:
        >>> tasks = get_daily_treatment_tasks(db)
        >>> print(f"Active: {len(tasks['active'])}")
        >>> print(f"Ending: {len(tasks['ending_today'])}")
        >>> print(f"Follow-ups: {len(tasks['followups_needed'])}")
    """
    return {
        "active": get_active_treatments(db),
        "ending_today": get_treatments_ending_today(db),
        "followups_needed": get_treatments_needing_followup(db),
        "date": get_today()
    }


def should_send_reminder(treatment: Treatment) -> bool:
    """
    Determine if reminder should be sent for a treatment.

    Args:
        treatment: Treatment object to check

    Returns:
        True if treatment is active and not ending today

    Example:
        >>> treatment = Treatment(status="active", end_date=None)
        >>> should_send_reminder(treatment)
        True
    """
    if treatment.status != "active":
        return False

    # Don't send reminder if treatment already ended
    if treatment.end_date and treatment.end_date < get_today():
        return False

    return True


def get_treatment_days_remaining(treatment: Treatment) -> Optional[int]:
    """
    Calculate days remaining in treatment.

    Args:
        treatment: Treatment object

    Returns:
        Number of days remaining, or None if ongoing (no end date)

    Example:
        >>> treatment = Treatment(
        ...     start_date=date(2026, 1, 1),
        ...     end_date=date(2026, 1, 10)
        ... )
        >>> days = get_treatment_days_remaining(treatment)
    """
    if not treatment.end_date:
        return None

    today = get_today()
    delta = treatment.end_date - today
    return max(0, delta.days)


def get_overdue_followups(db: Session, days_overdue: int = 2) -> List[Treatment]:
    """
    Get treatments with overdue follow-up assessments.

    Args:
        db: Database session
        days_overdue: Number of days past due (default 2)

    Returns:
        List of treatments missing follow-up assessments

    Example:
        >>> overdue = get_overdue_followups(db, days_overdue=3)
        >>> for t in overdue:
        ...     print(f"Treatment {t.id} follow-up is overdue")
    """
    today = get_today()
    cutoff_date = add_days(today, -(5 + days_overdue))

    # Find completed treatments that ended before cutoff and have no followup
    treatments = db.query(Treatment).filter(
        Treatment.end_date <= cutoff_date,
        Treatment.status == "completed"
    ).all()

    # Filter to only those without follow-up assessment
    overdue = []
    for treatment in treatments:
        if not treatment.followup_assessments:
            overdue.append(treatment)

    return overdue


def calculate_treatment_workload(db: Session) -> dict:
    """
    Calculate daily workload metrics.

    Args:
        db: Database session

    Returns:
        Dictionary with workload statistics

    Example:
        >>> workload = calculate_treatment_workload(db)
        >>> print(f"Total active: {workload['total_active']}")
        >>> print(f"Daily observations needed: {workload['observations_needed']}")
    """
    active = get_active_treatments(db)
    ending = get_treatments_ending_today(db)
    followups = get_treatments_needing_followup(db)

    return {
        "total_active": len(active),
        "ending_today": len(ending),
        "followups_today": len(followups),
        "observations_needed": len(active),
        "estimated_time_minutes": len(active) * 5 + len(followups) * 10
    }
