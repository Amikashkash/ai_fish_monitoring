"""
Filename: validators.py
Purpose: Data validation utilities for input sanitization
Author: Fish Monitoring System
Created: 2026-02-15

This module provides validation functions for user inputs,
ensuring data integrity and preventing invalid entries.

Dependencies:
    - None (pure validation functions)

Example:
    >>> from app.utils.validators import validate_source_country
    >>> validate_source_country("Thailand")
    True
"""

from typing import List


# Valid fish source countries
VALID_SOURCES: List[str] = [
    "Sri Lanka",
    "Thailand",
    "Singapore",
    "Malaysia",
    "Indonesia",
    "Philippines",
    "Vietnam",
    "China",
    "India",
    "Brazil"
]


def validate_source_country(source: str) -> bool:
    """
    Validate if source country is recognized.

    Args:
        source: Country name to validate

    Returns:
        True if valid, False otherwise

    Example:
        >>> validate_source_country("Sri Lanka")
        True
        >>> validate_source_country("Unknown Country")
        False
    """
    return source in VALID_SOURCES


def validate_condition_score(score: int) -> bool:
    """
    Validate fish condition score is within valid range (1-5).

    Args:
        score: Integer score to validate

    Returns:
        True if score is between 1 and 5 (inclusive)

    Example:
        >>> validate_condition_score(3)
        True
        >>> validate_condition_score(6)
        False
        >>> validate_condition_score(0)
        False
    """
    return 1 <= score <= 5


def validate_positive_number(value: float, allow_zero: bool = False) -> bool:
    """
    Validate that a number is positive.

    Args:
        value: Number to validate
        allow_zero: Whether to accept zero as valid (default False)

    Returns:
        True if valid positive number

    Example:
        >>> validate_positive_number(10.5)
        True
        >>> validate_positive_number(0)
        False
        >>> validate_positive_number(0, allow_zero=True)
        True
        >>> validate_positive_number(-5)
        False
    """
    if allow_zero:
        return value >= 0
    return value > 0


def validate_success_rate(rate: float) -> bool:
    """
    Validate success rate percentage is within 0-100 range.

    Args:
        rate: Success rate percentage to validate

    Returns:
        True if rate is between 0 and 100 (inclusive)

    Example:
        >>> validate_success_rate(85.5)
        True
        >>> validate_success_rate(100.0)
        True
        >>> validate_success_rate(150.0)
        False
        >>> validate_success_rate(-10.0)
        False
    """
    return 0 <= rate <= 100


def validate_quantity(quantity: int) -> bool:
    """
    Validate fish quantity is reasonable.

    Args:
        quantity: Number of fish to validate

    Returns:
        True if quantity is positive and reasonable (1-10000)

    Example:
        >>> validate_quantity(50)
        True
        >>> validate_quantity(0)
        False
        >>> validate_quantity(15000)
        False
    """
    return 1 <= quantity <= 10000


def validate_volume(volume: int) -> bool:
    """
    Validate aquarium volume is reasonable (in liters).

    Args:
        volume: Volume in liters to validate

    Returns:
        True if volume is reasonable (10-100000 liters)

    Example:
        >>> validate_volume(100)
        True
        >>> validate_volume(5)
        False
        >>> validate_volume(200000)
        False
    """
    return 10 <= volume <= 100000


def add_custom_source(source: str) -> bool:
    """
    Add a new source country to the valid sources list.

    Args:
        source: Country name to add

    Returns:
        True if added successfully, False if already exists

    Example:
        >>> add_custom_source("Australia")
        True
        >>> add_custom_source("Thailand")  # Already exists
        False
    """
    if source in VALID_SOURCES:
        return False

    VALID_SOURCES.append(source)
    return True


def get_valid_sources() -> List[str]:
    """
    Get list of all valid source countries.

    Returns:
        List of valid country names

    Example:
        >>> sources = get_valid_sources()
        >>> "Thailand" in sources
        True
    """
    return VALID_SOURCES.copy()
