"""
Filename: success_rate_calculator.py
Purpose: Calculate treatment success rates and survival statistics
Author: Fish Monitoring System
Created: 2026-02-15

This module provides utilities for calculating success rates,
survival percentages, and treatment effectiveness metrics.

Dependencies:
    - None (pure calculation functions)

Example:
    >>> from app.services.success_rate_calculator import calculate_success_rate
    >>> rate = calculate_success_rate(survived=48, total=50)
    >>> print(rate)  # Output: 96.0
"""

from typing import List, Dict, Tuple


def calculate_success_rate(survived: int, total: int) -> float:
    """
    Calculate survival success rate as percentage.

    Args:
        survived: Number of fish that survived
        total: Total number of fish

    Returns:
        Success rate as percentage (0-100), rounded to 2 decimal places

    Raises:
        ValueError: If total is zero or negative, or survived > total

    Example:
        >>> calculate_success_rate(48, 50)
        96.0
        >>> calculate_success_rate(50, 50)
        100.0
        >>> calculate_success_rate(0, 50)
        0.0
    """
    if total <= 0:
        raise ValueError("Total must be positive")

    if survived < 0:
        raise ValueError("Survived count cannot be negative")

    if survived > total:
        raise ValueError("Survived count cannot exceed total")

    rate = (survived / total) * 100
    return round(rate, 2)


def calculate_mortality_rate(survived: int, total: int) -> float:
    """
    Calculate mortality rate as percentage.

    Args:
        survived: Number of fish that survived
        total: Total number of fish

    Returns:
        Mortality rate as percentage (0-100)

    Example:
        >>> calculate_mortality_rate(48, 50)
        4.0
        >>> calculate_mortality_rate(50, 50)
        0.0
    """
    success_rate = calculate_success_rate(survived, total)
    return round(100.0 - success_rate, 2)


def assess_treatment_effectiveness(success_rate: float) -> str:
    """
    Assess treatment effectiveness based on success rate.

    Args:
        success_rate: Success rate percentage (0-100)

    Returns:
        Effectiveness rating: "excellent", "good", "fair", "poor"

    Example:
        >>> assess_treatment_effectiveness(95.0)
        'excellent'
        >>> assess_treatment_effectiveness(75.0)
        'fair'
        >>> assess_treatment_effectiveness(50.0)
        'poor'
    """
    if success_rate >= 90:
        return "excellent"
    elif success_rate >= 80:
        return "good"
    elif success_rate >= 70:
        return "fair"
    else:
        return "poor"


def calculate_average_success_rate(success_rates: List[float]) -> float:
    """
    Calculate average success rate from multiple treatments.

    Args:
        success_rates: List of success rate percentages

    Returns:
        Average success rate, rounded to 2 decimal places

    Example:
        >>> rates = [95.0, 88.0, 92.0]
        >>> calculate_average_success_rate(rates)
        91.67
    """
    if not success_rates:
        return 0.0

    average = sum(success_rates) / len(success_rates)
    return round(average, 2)


def calculate_weighted_success_rate(
    outcomes: List[Tuple[int, int]]
) -> float:
    """
    Calculate weighted success rate from multiple shipments.

    Weights each shipment by its size to get accurate overall rate.

    Args:
        outcomes: List of (survived, total) tuples for each shipment

    Returns:
        Weighted average success rate

    Example:
        >>> outcomes = [(48, 50), (95, 100), (18, 20)]
        >>> calculate_weighted_success_rate(outcomes)
        94.71
    """
    if not outcomes:
        return 0.0

    total_survived = sum(survived for survived, _ in outcomes)
    total_count = sum(total for _, total in outcomes)

    if total_count == 0:
        return 0.0

    return calculate_success_rate(total_survived, total_count)


def is_treatment_successful(
    success_rate: float,
    threshold: float = 80.0
) -> bool:
    """
    Determine if treatment met success threshold.

    Args:
        success_rate: Success rate percentage
        threshold: Minimum acceptable success rate (default 80%)

    Returns:
        True if success_rate >= threshold

    Example:
        >>> is_treatment_successful(85.0)
        True
        >>> is_treatment_successful(75.0)
        False
        >>> is_treatment_successful(75.0, threshold=70.0)
        True
    """
    return success_rate >= threshold


def calculate_loss_count(survived: int, total: int) -> int:
    """
    Calculate number of fish lost during treatment.

    Args:
        survived: Number of fish that survived
        total: Total number of fish

    Returns:
        Number of fish that died

    Example:
        >>> calculate_loss_count(48, 50)
        2
        >>> calculate_loss_count(50, 50)
        0
    """
    return total - survived


def get_success_rate_category(success_rate: float) -> Dict[str, any]:
    """
    Get detailed categorization of success rate.

    Args:
        success_rate: Success rate percentage

    Returns:
        Dictionary with category, description, and recommendation

    Example:
        >>> info = get_success_rate_category(95.0)
        >>> info['category']
        'excellent'
        >>> info['recommendation']
        'Protocol highly effective, recommend for future use'
    """
    if success_rate >= 90:
        return {
            "category": "excellent",
            "description": "Outstanding survival rate",
            "recommendation": "Protocol highly effective, recommend for future use",
            "should_repeat": True
        }
    elif success_rate >= 80:
        return {
            "category": "good",
            "description": "Good survival rate",
            "recommendation": "Protocol effective, suitable for reuse",
            "should_repeat": True
        }
    elif success_rate >= 70:
        return {
            "category": "fair",
            "description": "Acceptable survival rate",
            "recommendation": "Protocol moderately effective, consider improvements",
            "should_repeat": True
        }
    else:
        return {
            "category": "poor",
            "description": "Below acceptable survival rate",
            "recommendation": "Protocol needs significant modification",
            "should_repeat": False
        }
