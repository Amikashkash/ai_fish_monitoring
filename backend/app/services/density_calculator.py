"""
Filename: density_calculator.py
Purpose: Calculate fish density in aquariums to assess health risk factors
Author: Fish Monitoring System
Created: 2026-02-15

This module provides utilities for calculating fish density (fish per liter)
which is a critical factor in fish health during acclimation period.

Dependencies:
    - None (pure calculation functions)

Example:
    >>> from app.services.density_calculator import calculate_density
    >>> density = calculate_density(quantity=10, volume=100)
    >>> print(density)  # Output: 0.1
"""


def calculate_density(quantity: int, volume: int) -> float:
    """
    Calculate fish density (fish per liter) for health assessment.

    Density is a key health indicator:
    - < 0.1: Low risk, optimal conditions
    - 0.1-0.2: Medium risk, monitor closely
    - > 0.2: High risk, requires intensive treatment

    Args:
        quantity (int): Number of fish in the aquarium
        volume (int): Aquarium volume in liters

    Returns:
        float: Fish density (fish per liter), rounded to 2 decimal places

    Raises:
        ValueError: If volume is zero or negative

    Example:
        >>> calculate_density(10, 100)
        0.1
        >>> calculate_density(25, 50)
        0.5
        >>> calculate_density(0, 100)
        0.0
    """
    if volume <= 0:
        raise ValueError("Volume must be positive")

    if quantity < 0:
        raise ValueError("Quantity cannot be negative")

    density = quantity / volume
    return round(density, 2)


def assess_density_risk(density: float) -> str:
    """
    Assess health risk level based on fish density.

    Args:
        density: Fish per liter ratio

    Returns:
        Risk level: "low", "medium", or "high"

    Example:
        >>> assess_density_risk(0.05)
        'low'
        >>> assess_density_risk(0.15)
        'medium'
        >>> assess_density_risk(0.30)
        'high'
    """
    if density < 0.1:
        return "low"
    elif density < 0.2:
        return "medium"
    else:
        return "high"


def recommend_treatment_intensity(density: float) -> str:
    """
    Recommend treatment intensity based on density.

    Args:
        density: Fish per liter ratio

    Returns:
        Treatment recommendation string

    Example:
        >>> recommend_treatment_intensity(0.05)
        'Standard monitoring protocol'
        >>> recommend_treatment_intensity(0.15)
        'Enhanced monitoring, daily observations critical'
        >>> recommend_treatment_intensity(0.30)
        'Intensive treatment required, consider splitting into multiple tanks'
    """
    risk = assess_density_risk(density)

    recommendations = {
        "low": "Standard monitoring protocol",
        "medium": "Enhanced monitoring, daily observations critical",
        "high": "Intensive treatment required, consider splitting into multiple tanks"
    }

    return recommendations[risk]


def calculate_recommended_volume(quantity: int, target_density: float = 0.1) -> int:
    """
    Calculate recommended aquarium volume for target density.

    Args:
        quantity: Number of fish
        target_density: Desired fish per liter ratio (default 0.1 for low risk)

    Returns:
        Recommended volume in liters

    Example:
        >>> calculate_recommended_volume(50)
        500
        >>> calculate_recommended_volume(50, target_density=0.05)
        1000
    """
    if target_density <= 0:
        raise ValueError("Target density must be positive")

    recommended_volume = quantity / target_density
    return int(recommended_volume)


def is_overcrowded(quantity: int, volume: int, threshold: float = 0.2) -> bool:
    """
    Check if aquarium is overcrowded based on density threshold.

    Args:
        quantity: Number of fish
        volume: Aquarium volume in liters
        threshold: Density threshold for overcrowding (default 0.2)

    Returns:
        True if density exceeds threshold

    Example:
        >>> is_overcrowded(30, 100)
        True
        >>> is_overcrowded(10, 100)
        False
    """
    density = calculate_density(quantity, volume)
    return density > threshold
