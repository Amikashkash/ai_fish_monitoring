"""
Filename: date_helpers.py
Purpose: Date utility functions for treatment scheduling
Author: Fish Monitoring System
Created: 2026-02-15

This module provides date manipulation utilities for calculating
treatment periods, follow-up dates, and scheduling tasks.

Dependencies:
    - datetime: Standard Python date/time handling

Example:
    >>> from app.utils.date_helpers import add_days
    >>> from datetime import date
    >>> new_date = add_days(date(2026, 1, 1), 5)
    >>> print(new_date)  # 2026-01-06
"""

from datetime import datetime, timedelta, date
from typing import Optional


def add_days(start_date: date, days: int) -> date:
    """
    Add specified number of days to a date.

    Args:
        start_date: Starting date
        days: Number of days to add (can be negative to subtract)

    Returns:
        New date object with days added

    Example:
        >>> start = date(2026, 1, 1)
        >>> end = add_days(start, 5)
        >>> print(end)
        2026-01-06
        >>> earlier = add_days(start, -3)
        >>> print(earlier)
        2025-12-29
    """
    return start_date + timedelta(days=days)


def get_followup_date(treatment_end_date: date) -> date:
    """
    Calculate 5-day follow-up date after treatment ends.

    Args:
        treatment_end_date: Date when treatment was completed

    Returns:
        Date for follow-up assessment (treatment_end + 5 days)

    Example:
        >>> end = date(2026, 1, 10)
        >>> followup = get_followup_date(end)
        >>> print(followup)
        2026-01-15
    """
    return add_days(treatment_end_date, 5)


def days_between(start_date: date, end_date: date) -> int:
    """
    Calculate number of days between two dates.

    Args:
        start_date: Starting date
        end_date: Ending date

    Returns:
        Number of days between dates (positive if end > start)

    Example:
        >>> start = date(2026, 1, 1)
        >>> end = date(2026, 1, 10)
        >>> days_between(start, end)
        9
        >>> days_between(end, start)
        -9
    """
    delta = end_date - start_date
    return delta.days


def is_treatment_day(observation_date: date, start_date: date, end_date: Optional[date]) -> bool:
    """
    Check if a given date falls within the treatment period.

    Args:
        observation_date: Date to check
        start_date: Treatment start date
        end_date: Treatment end date (None if ongoing)

    Returns:
        True if observation_date is within treatment period

    Example:
        >>> start = date(2026, 1, 1)
        >>> end = date(2026, 1, 10)
        >>> is_treatment_day(date(2026, 1, 5), start, end)
        True
        >>> is_treatment_day(date(2026, 1, 15), start, end)
        False
        >>> is_treatment_day(date(2026, 1, 5), start, None)  # Ongoing
        True
    """
    if observation_date < start_date:
        return False

    if end_date is None:
        # Treatment is ongoing
        return True

    return observation_date <= end_date


def get_today() -> date:
    """
    Get today's date.

    Returns:
        Current date

    Example:
        >>> today = get_today()
        >>> isinstance(today, date)
        True
    """
    return date.today()


def format_date_for_display(d: date) -> str:
    """
    Format date for user-friendly display.

    Args:
        d: Date to format

    Returns:
        Formatted date string (e.g., "15 Feb 2026")

    Example:
        >>> d = date(2026, 2, 15)
        >>> format_date_for_display(d)
        '15 Feb 2026'
    """
    return d.strftime("%d %b %Y")


def parse_date_string(date_string: str, format: str = "%Y-%m-%d") -> Optional[date]:
    """
    Parse date string into date object.

    Args:
        date_string: Date as string
        format: Date format (default ISO format YYYY-MM-DD)

    Returns:
        Parsed date object, or None if parsing fails

    Example:
        >>> parse_date_string("2026-02-15")
        datetime.date(2026, 2, 15)
        >>> parse_date_string("15/02/2026", format="%d/%m/%Y")
        datetime.date(2026, 2, 15)
        >>> parse_date_string("invalid")
        None
    """
    try:
        return datetime.strptime(date_string, format).date()
    except (ValueError, TypeError):
        return None


def get_treatment_duration(start_date: date, end_date: Optional[date]) -> int:
    """
    Calculate treatment duration in days.

    Args:
        start_date: Treatment start date
        end_date: Treatment end date (None if ongoing)

    Returns:
        Number of days in treatment (0 if ongoing)

    Example:
        >>> start = date(2026, 1, 1)
        >>> end = date(2026, 1, 8)
        >>> get_treatment_duration(start, end)
        7
        >>> get_treatment_duration(start, None)
        0  # Ongoing
    """
    if end_date is None:
        return 0

    return days_between(start_date, end_date)


def is_past_due(target_date: date, reference_date: Optional[date] = None) -> bool:
    """
    Check if a target date is in the past.

    Args:
        target_date: Date to check
        reference_date: Reference date (default: today)

    Returns:
        True if target_date < reference_date

    Example:
        >>> target = date(2026, 1, 1)
        >>> is_past_due(target, reference_date=date(2026, 1, 5))
        True
        >>> is_past_due(date(2026, 12, 31), reference_date=date(2026, 1, 1))
        False
    """
    if reference_date is None:
        reference_date = get_today()

    return target_date < reference_date
