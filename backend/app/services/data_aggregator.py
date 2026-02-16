"""
Filename: data_aggregator.py
Purpose: Aggregate and prepare historical data for AI analysis
Author: Fish Monitoring System
Created: 2026-02-15

This module provides functions for aggregating treatment data,
building historical contexts, and preparing data for AI learning.

Dependencies:
    - sqlalchemy.orm: Database session
    - app.models: Database models
    - typing: Type hints

Example:
    >>> from app.services.data_aggregator import aggregate_historical_data
    >>> data = aggregate_historical_data(db, "Betta splendens", "Thailand")
"""

from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from app.models.shipment import Shipment
from app.models.treatment import Treatment, TreatmentDrug
from app.models.observation import DailyObservation
from app.models.followup import FollowupAssessment
from app.models.drug_protocol import DrugProtocol


def aggregate_historical_data(
    db: Session,
    scientific_name: str,
    source_country: str
) -> Dict:
    """
    Aggregate all historical data for a fish/source combination.

    This prepares comprehensive data for AI learning and recommendations.

    Args:
        db: Database session
        scientific_name: Fish species scientific name
        source_country: Source country name

    Returns:
        Dictionary with aggregated historical data

    Example:
        >>> data = aggregate_historical_data(db, "Betta splendens", "Thailand")
        >>> print(data['shipment_count'])
        10
        >>> print(data['avg_success_rate'])
        92.5
    """
    # Get all shipments for this combination
    shipments = db.query(Shipment).filter(
        Shipment.scientific_name == scientific_name,
        Shipment.source == source_country
    ).all()

    if not shipments:
        return {
            "shipment_count": 0,
            "scientific_name": scientific_name,
            "source_country": source_country,
            "avg_success_rate": None,
            "treatments": [],
            "successful_protocols": []
        }

    # Collect treatment data
    all_treatments = []
    successful_protocols = []

    for shipment in shipments:
        for treatment in shipment.treatments:
            treatment_data = build_treatment_summary(db, treatment)
            all_treatments.append(treatment_data)

            # If treatment was successful, record the protocol
            if treatment_data.get("success_rate", 0) >= 80:
                protocol = extract_protocol(db, treatment)
                if protocol:
                    successful_protocols.append(protocol)

    # Calculate aggregated metrics
    success_rates = [t["success_rate"] for t in all_treatments if t.get("success_rate")]
    avg_success_rate = (
        sum(success_rates) / len(success_rates)
        if success_rates else None
    )

    return {
        "shipment_count": len(shipments),
        "scientific_name": scientific_name,
        "source_country": source_country,
        "avg_success_rate": round(avg_success_rate, 2) if avg_success_rate else None,
        "treatments": all_treatments,
        "successful_protocols": successful_protocols,
        "total_fish": sum(s.quantity for s in shipments),
        "avg_density": calculate_avg_density(shipments)
    }


def build_treatment_summary(db: Session, treatment: Treatment) -> Dict:
    """
    Build comprehensive summary of a treatment.

    Args:
        db: Database session
        treatment: Treatment object

    Returns:
        Dictionary with treatment details

    Example:
        >>> summary = build_treatment_summary(db, treatment)
        >>> print(summary['drugs_used'])
        ['Methylene Blue', 'Aquarium Salt']
    """
    # Get shipment details
    shipment = treatment.shipment

    # Get drugs used
    drugs_used = []
    for td in treatment.treatment_drugs:
        drug = db.query(DrugProtocol).get(td.drug_protocol_id)
        if drug:
            drugs_used.append({
                "name": drug.drug_name,
                "dosage": float(td.actual_dosage) if td.actual_dosage else None,
                "frequency": td.actual_frequency
            })

    # Get follow-up if exists
    followup = treatment.followup_assessments[0] if treatment.followup_assessments else None

    # Get daily observations
    observations = treatment.daily_observations
    symptom_counts = count_symptoms(observations)

    return {
        "treatment_id": treatment.id,
        "shipment_id": shipment.id,
        "fish_quantity": shipment.quantity,
        "density": float(shipment.density) if shipment.density else None,
        "drugs_used": drugs_used,
        "treatment_duration_days": (
            (treatment.end_date - treatment.start_date).days
            if treatment.end_date else None
        ),
        "success_rate": float(followup.success_rate) if followup and followup.success_rate else None,
        "symptom_counts": symptom_counts,
        "overall_condition_avg": calculate_avg_condition(observations)
    }


def extract_protocol(db: Session, treatment: Treatment) -> Optional[Dict]:
    """
    Extract treatment protocol details for successful treatments.

    Args:
        db: Database session
        treatment: Treatment object

    Returns:
        Protocol dictionary or None

    Example:
        >>> protocol = extract_protocol(db, treatment)
        >>> print(protocol['drugs'])
        [{'name': 'Methylene Blue', 'dosage': 2.0}]
    """
    drugs = []
    for td in treatment.treatment_drugs:
        drug = db.query(DrugProtocol).get(td.drug_protocol_id)
        if drug:
            drugs.append({
                "name": drug.drug_name,
                "dosage": float(td.actual_dosage) if td.actual_dosage else None,
                "unit": drug.dosage_unit,
                "frequency": td.actual_frequency
            })

    if not drugs:
        return None

    return {
        "drugs": drugs,
        "duration_days": (
            (treatment.end_date - treatment.start_date).days
            if treatment.end_date else None
        )
    }


def count_symptoms(observations: List[DailyObservation]) -> Dict:
    """
    Count symptom occurrences across observations.

    Args:
        observations: List of DailyObservation objects

    Returns:
        Dictionary with symptom counts

    Example:
        >>> counts = count_symptoms(observations)
        >>> print(counts['lethargy'])
        3
    """
    return {
        "lethargy": sum(1 for o in observations if o.symptoms_lethargy),
        "loss_of_appetite": sum(1 for o in observations if o.symptoms_loss_of_appetite),
        "spots": sum(1 for o in observations if o.symptoms_spots),
        "fin_damage": sum(1 for o in observations if o.symptoms_fin_damage),
        "breathing_issues": sum(1 for o in observations if o.symptoms_breathing_issues)
    }


def calculate_avg_condition(observations: List[DailyObservation]) -> Optional[float]:
    """
    Calculate average condition score from observations.

    Args:
        observations: List of DailyObservation objects

    Returns:
        Average condition score or None

    Example:
        >>> avg = calculate_avg_condition(observations)
        >>> print(avg)
        3.8
    """
    scores = [o.overall_condition_score for o in observations if o.overall_condition_score]

    if not scores:
        return None

    return round(sum(scores) / len(scores), 2)


def calculate_avg_density(shipments: List[Shipment]) -> Optional[float]:
    """
    Calculate average density across shipments.

    Args:
        shipments: List of Shipment objects

    Returns:
        Average density or None

    Example:
        >>> avg = calculate_avg_density(shipments)
        >>> print(avg)
        0.12
    """
    densities = [float(s.density) for s in shipments if s.density]

    if not densities:
        return None

    return round(sum(densities) / len(densities), 2)


def get_treatment_timeline(db: Session, treatment_id: int) -> List[Dict]:
    """
    Build timeline of events for a treatment.

    Args:
        db: Database session
        treatment_id: Treatment ID

    Returns:
        List of timeline events sorted by date

    Example:
        >>> timeline = get_treatment_timeline(db, 1)
        >>> for event in timeline:
        ...     print(f"{event['date']}: {event['description']}")
    """
    treatment = db.query(Treatment).get(treatment_id)
    if not treatment:
        return []

    timeline = []

    # Treatment start
    timeline.append({
        "date": treatment.start_date,
        "type": "treatment_start",
        "description": "Treatment started"
    })

    # Daily observations
    for obs in treatment.daily_observations:
        timeline.append({
            "date": obs.observation_date,
            "type": "observation",
            "description": f"Observation - Score: {obs.overall_condition_score}",
            "data": {
                "score": obs.overall_condition_score,
                "has_symptoms": obs.has_symptoms()
            }
        })

    # Treatment end
    if treatment.end_date:
        timeline.append({
            "date": treatment.end_date,
            "type": "treatment_end",
            "description": "Treatment ended"
        })

    # Follow-up
    if treatment.followup_assessments:
        for followup in treatment.followup_assessments:
            timeline.append({
                "date": followup.followup_date,
                "type": "followup",
                "description": f"Follow-up - Success: {followup.success_rate}%",
                "data": {
                    "success_rate": float(followup.success_rate) if followup.success_rate else None,
                    "stability_score": followup.stability_score
                }
            })

    # Sort by date
    timeline.sort(key=lambda x: x["date"])

    return timeline
