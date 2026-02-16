"""
Filename: formatters.py
Purpose: Data formatting utilities for consistent output
Author: Fish Monitoring System
Created: 2026-02-15

This module provides formatting functions for displaying data
in user-friendly formats (dosages, percentages, etc.).

Dependencies:
    - None (pure formatting functions)

Example:
    >>> from app.utils.formatters import format_drug_dosage
    >>> format_drug_dosage(2.5, "mg/L")
    '2.5 mg/L'
"""

from typing import Optional
from decimal import Decimal


def format_drug_dosage(dosage: float, unit: str) -> str:
    """
    Format drug dosage with unit for display.

    Args:
        dosage: Dosage amount
        unit: Unit of measurement (e.g., "mg/L", "ml/10L")

    Returns:
        Formatted dosage string

    Example:
        >>> format_drug_dosage(2.5, "mg/L")
        '2.5 mg/L'
        >>> format_drug_dosage(10.0, "drops/gallon")
        '10.0 drops/gallon'
    """
    return f"{dosage} {unit}"


def format_percentage(value: float, decimal_places: int = 1) -> str:
    """
    Format a number as percentage.

    Args:
        value: Value to format (0-100)
        decimal_places: Number of decimal places (default 1)

    Returns:
        Formatted percentage string

    Example:
        >>> format_percentage(85.5)
        '85.5%'
        >>> format_percentage(100.0)
        '100.0%'
        >>> format_percentage(92.33333, decimal_places=2)
        '92.33%'
    """
    return f"{value:.{decimal_places}f}%"


def format_density(density: float) -> str:
    """
    Format fish density for display.

    Args:
        density: Fish per liter ratio

    Returns:
        Formatted density string with interpretation

    Example:
        >>> format_density(0.05)
        '0.05 fish/L (Low risk)'
        >>> format_density(0.15)
        '0.15 fish/L (Medium risk)'
        >>> format_density(0.25)
        '0.25 fish/L (High risk)'
    """
    risk_level = get_density_risk_level(density)
    return f"{density:.2f} fish/L ({risk_level})"


def get_density_risk_level(density: float) -> str:
    """
    Determine risk level based on fish density.

    Args:
        density: Fish per liter ratio

    Returns:
        Risk level string

    Example:
        >>> get_density_risk_level(0.05)
        'Low risk'
        >>> get_density_risk_level(0.15)
        'Medium risk'
        >>> get_density_risk_level(0.30)
        'High risk'
    """
    if density < 0.1:
        return "Low risk"
    elif density < 0.2:
        return "Medium risk"
    else:
        return "High risk"


def format_currency(amount: float, currency: str = "$") -> str:
    """
    Format monetary amount.

    Args:
        amount: Amount to format
        currency: Currency symbol (default "$")

    Returns:
        Formatted currency string

    Example:
        >>> format_currency(25.50)
        '$25.50'
        >>> format_currency(1000.0, "€")
        '€1000.00'
    """
    return f"{currency}{amount:.2f}"


def format_score_description(score: int) -> str:
    """
    Get text description of condition/stability score (1-5).

    Args:
        score: Score from 1 to 5

    Returns:
        Text description of score

    Example:
        >>> format_score_description(5)
        'Excellent'
        >>> format_score_description(3)
        'Fair'
        >>> format_score_description(1)
        'Critical'
    """
    descriptions = {
        5: "Excellent",
        4: "Good",
        3: "Fair",
        2: "Poor",
        1: "Critical"
    }
    return descriptions.get(score, "Unknown")


def format_confidence_level(confidence: str) -> str:
    """
    Format confidence level with emoji indicator.

    Args:
        confidence: Confidence level string

    Returns:
        Formatted confidence string with indicator

    Example:
        >>> format_confidence_level("high")
        '✓ High confidence'
        >>> format_confidence_level("no_data")
        '! No historical data'
    """
    indicators = {
        "high": "✓ High confidence",
        "medium": "~ Medium confidence",
        "low": "⚠ Low confidence",
        "no_data": "! No historical data"
    }
    return indicators.get(confidence, confidence)


def format_treatment_status(status: str) -> str:
    """
    Format treatment status for display.

    Args:
        status: Status string (active, completed, modified)

    Returns:
        Formatted status string

    Example:
        >>> format_treatment_status("active")
        'Active'
        >>> format_treatment_status("completed")
        'Completed'
    """
    return status.capitalize()


def format_fish_count(survived: int, total: int) -> str:
    """
    Format fish count with survival indication.

    Args:
        survived: Number of fish that survived
        total: Total number of fish

    Returns:
        Formatted count string

    Example:
        >>> format_fish_count(48, 50)
        '48/50 fish survived'
        >>> format_fish_count(50, 50)
        '50/50 fish survived (100%)'
    """
    if survived == total:
        return f"{survived}/{total} fish survived (100%)"
    else:
        percentage = (survived / total * 100) if total > 0 else 0
        return f"{survived}/{total} fish survived ({percentage:.1f}%)"


def format_source_display(source: str) -> str:
    """
    Format source country for consistent display.

    Args:
        source: Source country name

    Returns:
        Formatted source string

    Example:
        >>> format_source_display("thailand")
        'Thailand'
        >>> format_source_display("SRI LANKA")
        'Sri Lanka'
    """
    # Capitalize each word
    return source.title()


def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Truncate text to maximum length with suffix.

    Args:
        text: Text to truncate
        max_length: Maximum length (default 50)
        suffix: Suffix to add if truncated (default "...")

    Returns:
        Truncated text

    Example:
        >>> truncate_text("This is a very long text that should be truncated", 20)
        'This is a very lo...'
        >>> truncate_text("Short text", 20)
        'Short text'
    """
    if len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix
