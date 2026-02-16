"""
Filename: supplier_analyzer.py
Purpose: Analyze supplier performance and reliability
Author: Fish Monitoring System
Created: 2026-02-15

This module provides functions for analyzing supplier success rates,
ranking suppliers, and recommending best sources for fish.

Dependencies:
    - sqlalchemy.orm: Database session
    - app.models: Database models
    - app.services.success_rate_calculator: Success rate utilities

Example:
    >>> from app.services.supplier_analyzer import analyze_supplier_performance
    >>> scores = analyze_supplier_performance(db)
"""

from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.shipment import Shipment
from app.models.treatment import Treatment
from app.models.followup import FollowupAssessment
from app.services.success_rate_calculator import calculate_average_success_rate


def analyze_supplier_performance(db: Session) -> List[Dict]:
    """
    Analyze performance for all suppliers.

    Args:
        db: Database session

    Returns:
        List of supplier performance dictionaries, sorted by success rate

    Example:
        >>> suppliers = analyze_supplier_performance(db)
        >>> for s in suppliers:
        ...     print(f"{s['source']}: {s['avg_success_rate']}%")
    """
    # Query all unique sources
    sources = db.query(Shipment.source).distinct().all()

    supplier_stats = []
    for (source,) in sources:
        stats = get_supplier_stats(db, source)
        if stats['shipment_count'] > 0:
            supplier_stats.append(stats)

    # Sort by success rate (descending)
    supplier_stats.sort(key=lambda x: x['avg_success_rate'], reverse=True)

    return supplier_stats


def get_supplier_stats(db: Session, source: str) -> Dict:
    """
    Get detailed statistics for a specific supplier.

    Args:
        db: Database session
        source: Supplier/source country name

    Returns:
        Dictionary with supplier statistics

    Example:
        >>> stats = get_supplier_stats(db, "Thailand")
        >>> print(stats['avg_success_rate'])
        92.5
    """
    # Get all shipments from this source
    shipments = db.query(Shipment).filter(
        Shipment.source == source
    ).all()

    if not shipments:
        return {
            "source": source,
            "shipment_count": 0,
            "avg_success_rate": 0.0,
            "total_fish": 0,
            "species_count": 0,
            "rating": "no_data"
        }

    shipment_ids = [s.id for s in shipments]

    # Get treatments for these shipments
    treatments = db.query(Treatment).filter(
        Treatment.shipment_id.in_(shipment_ids)
    ).all()

    # Get follow-up assessments
    treatment_ids = [t.id for t in treatments]
    followups = db.query(FollowupAssessment).filter(
        FollowupAssessment.treatment_id.in_(treatment_ids)
    ).all()

    # Calculate statistics
    success_rates = [f.success_rate for f in followups if f.success_rate is not None]
    avg_success_rate = calculate_average_success_rate(success_rates) if success_rates else 0.0

    total_fish = sum(s.quantity for s in shipments)
    unique_species = len(set(s.scientific_name for s in shipments))

    return {
        "source": source,
        "shipment_count": len(shipments),
        "avg_success_rate": avg_success_rate,
        "total_fish": total_fish,
        "species_count": unique_species,
        "rating": rate_supplier(avg_success_rate, len(shipments))
    }


def rate_supplier(avg_success_rate: float, sample_size: int) -> str:
    """
    Rate supplier based on success rate and sample size.

    Args:
        avg_success_rate: Average success rate percentage
        sample_size: Number of shipments

    Returns:
        Rating: "excellent", "good", "fair", "poor", or "insufficient_data"

    Example:
        >>> rate_supplier(95.0, 10)
        'excellent'
        >>> rate_supplier(85.0, 2)
        'insufficient_data'
    """
    if sample_size < 3:
        return "insufficient_data"

    if avg_success_rate >= 90:
        return "excellent"
    elif avg_success_rate >= 80:
        return "good"
    elif avg_success_rate >= 70:
        return "fair"
    else:
        return "poor"


def get_best_source_for_species(db: Session, scientific_name: str) -> Optional[Dict]:
    """
    Find best supplier for a specific fish species.

    Args:
        db: Database session
        scientific_name: Scientific name of fish species

    Returns:
        Dictionary with best source info, or None if no data

    Example:
        >>> best = get_best_source_for_species(db, "Betta splendens")
        >>> print(best['source'])
        'Thailand'
    """
    # Get all sources for this species
    sources = db.query(Shipment.source).filter(
        Shipment.scientific_name == scientific_name
    ).distinct().all()

    if not sources:
        return None

    source_stats = []
    for (source,) in sources:
        stats = get_source_species_stats(db, source, scientific_name)
        if stats['shipment_count'] > 0:
            source_stats.append(stats)

    if not source_stats:
        return None

    # Sort by success rate
    source_stats.sort(key=lambda x: x['avg_success_rate'], reverse=True)

    return source_stats[0] if source_stats else None


def get_source_species_stats(
    db: Session,
    source: str,
    scientific_name: str
) -> Dict:
    """
    Get statistics for specific source-species combination.

    Args:
        db: Database session
        source: Supplier/source country
        scientific_name: Fish species scientific name

    Returns:
        Dictionary with statistics

    Example:
        >>> stats = get_source_species_stats(db, "Thailand", "Betta splendens")
        >>> print(stats['avg_success_rate'])
        94.0
    """
    shipments = db.query(Shipment).filter(
        Shipment.source == source,
        Shipment.scientific_name == scientific_name
    ).all()

    if not shipments:
        return {
            "source": source,
            "scientific_name": scientific_name,
            "shipment_count": 0,
            "avg_success_rate": 0.0
        }

    shipment_ids = [s.id for s in shipments]
    treatments = db.query(Treatment).filter(
        Treatment.shipment_id.in_(shipment_ids)
    ).all()

    treatment_ids = [t.id for t in treatments]
    followups = db.query(FollowupAssessment).filter(
        FollowupAssessment.treatment_id.in_(treatment_ids)
    ).all()

    success_rates = [f.success_rate for f in followups if f.success_rate is not None]
    avg_success_rate = calculate_average_success_rate(success_rates) if success_rates else 0.0

    return {
        "source": source,
        "scientific_name": scientific_name,
        "shipment_count": len(shipments),
        "avg_success_rate": avg_success_rate,
        "total_fish": sum(s.quantity for s in shipments)
    }


def compare_suppliers(db: Session, sources: List[str]) -> List[Dict]:
    """
    Compare multiple suppliers side by side.

    Args:
        db: Database session
        sources: List of supplier names to compare

    Returns:
        List of supplier statistics for comparison

    Example:
        >>> comparison = compare_suppliers(db, ["Thailand", "Sri Lanka"])
        >>> for s in comparison:
        ...     print(f"{s['source']}: {s['avg_success_rate']}%")
    """
    comparisons = []
    for source in sources:
        stats = get_supplier_stats(db, source)
        comparisons.append(stats)

    return comparisons


def get_supplier_recommendation(stats: Dict) -> str:
    """
    Get recommendation text based on supplier stats.

    Args:
        stats: Supplier statistics dictionary

    Returns:
        Recommendation text

    Example:
        >>> stats = {"avg_success_rate": 95.0, "shipment_count": 10}
        >>> rec = get_supplier_recommendation(stats)
        >>> print(rec)
        'Highly recommended supplier with excellent track record'
    """
    rating = stats.get("rating", "no_data")

    recommendations = {
        "excellent": "Highly recommended supplier with excellent track record",
        "good": "Reliable supplier, recommended for regular use",
        "fair": "Acceptable supplier, but monitor closely",
        "poor": "Not recommended - consider alternative sources",
        "insufficient_data": "Insufficient data for recommendation - proceed with caution",
        "no_data": "No historical data available"
    }

    return recommendations.get(rating, "No data available")
