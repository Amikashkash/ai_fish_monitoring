"""
Filename: prompt_builder.py
Purpose: Build formatted context strings for AI prompts
Author: Fish Monitoring System
Created: 2026-02-15

This module provides utilities for converting database records into
human-readable context strings for AI prompts. Ensures consistent
formatting across all AI features.

Dependencies:
    - app.models: Database models

Example:
    >>> from app.ai.prompt_builder import build_historical_context
    >>> context = build_historical_context(knowledge_record)
    >>> prompt = f"Historical data:\n{context}\n\nQuestion: ..."
"""

from typing import List

from app.models.ai_knowledge import AIKnowledge
from app.models.shipment import Shipment
from app.models.treatment import Treatment


def build_historical_context(knowledge: AIKnowledge) -> str:
    """
    Format AI knowledge record into readable context string.

    Converts structured database record into natural language
    description suitable for inclusion in AI prompts.

    Args:
        knowledge: AIKnowledge database record

    Returns:
        Formatted multi-line string with historical data

    Example:
        >>> context = build_historical_context(knowledge)
        >>> print(context)
        Source: Thailand
        Species: Betta splendens
        Previous Shipments: 10
        Success Rate: 85.5%
    """
    lines = [
        f"Source: {knowledge.source_country}",
        f"Species: {knowledge.scientific_name}",
        f"Previous Shipments: {knowledge.sample_size}",
        f"Success Rate: {knowledge.success_rate}%",
    ]

    if knowledge.successful_protocols:
        lines.append("\nSuccessful Protocols:")
        if isinstance(knowledge.successful_protocols, dict):
            for key, value in knowledge.successful_protocols.items():
                lines.append(f"  - {key}: {value}")
        else:
            lines.append(f"  {knowledge.successful_protocols}")

    if knowledge.insights:
        lines.append("\nKey Insights:")
        lines.append(knowledge.insights)

    return "\n".join(lines)


def build_shipment_summary(shipment: Shipment) -> str:
    """
    Format shipment details for AI prompt.

    Creates concise summary of shipment characteristics
    relevant to treatment decisions.

    Args:
        shipment: Shipment database record

    Returns:
        Formatted shipment summary string

    Example:
        >>> summary = build_shipment_summary(shipment)
        >>> print(summary)
        Shipment Details:
        - Species: Betta splendens (Siamese Fighting Fish)
        - Source: Thailand
        - Quantity: 50 fish
    """
    return f"""Shipment Details:
- Species: {shipment.scientific_name} ({shipment.common_name})
- Source: {shipment.source}
- Quantity: {shipment.quantity} fish
- Volume: {shipment.aquarium_volume_liters}L
- Density: {shipment.density} fish/L
- Fish Size: {shipment.fish_size or 'Not specified'}"""


def build_treatment_summary(
    treatment: Treatment,
    include_observations: bool = True
) -> str:
    """
    Format treatment details for AI analysis.

    Creates summary of treatment protocol and outcomes,
    optionally including observation data.

    Args:
        treatment: Treatment database record
        include_observations: Whether to include observation details

    Returns:
        Formatted treatment summary string

    Example:
        >>> summary = build_treatment_summary(treatment)
        >>> print(summary)
        Treatment Details:
        - Start Date: 2026-01-15
        - End Date: 2026-01-20
        - Status: completed
    """
    lines = [
        "Treatment Details:",
        f"- Start Date: {treatment.start_date}",
    ]

    if treatment.end_date:
        lines.append(f"- End Date: {treatment.end_date}")
        duration = (treatment.end_date - treatment.start_date).days
        lines.append(f"- Duration: {duration} days")

    lines.append(f"- Status: {treatment.status}")

    if hasattr(treatment, 'treatment_drugs') and treatment.treatment_drugs:
        lines.append("\nDrug Protocols:")
        for td in treatment.treatment_drugs:
            drug_name = td.drug_protocol.drug_name if hasattr(td, 'drug_protocol') else "Unknown"
            lines.append(
                f"  - {drug_name}: {td.actual_dosage} "
                f"({td.actual_frequency})"
            )

    if include_observations and hasattr(treatment, 'observations'):
        if treatment.observations:
            lines.append(f"\nObservations: {len(treatment.observations)} recorded")
            symptomatic_count = sum(
                1 for obs in treatment.observations
                if obs.has_symptoms()
            )
            lines.append(f"  - Days with symptoms: {symptomatic_count}")

    return "\n".join(lines)


def build_multiple_shipments_context(
    shipments: List[Shipment],
    max_shipments: int = 10
) -> str:
    """
    Format multiple shipment records for comparison.

    Creates summary table of historical shipments,
    limited to most recent entries.

    Args:
        shipments: List of Shipment records
        max_shipments: Maximum number to include (default 10)

    Returns:
        Formatted table string
    """
    limited_shipments = shipments[:max_shipments]
    lines = [f"Recent Shipments ({len(limited_shipments)}):"]

    for i, shipment in enumerate(limited_shipments, 1):
        lines.append(
            f"{i}. {shipment.date} | {shipment.scientific_name} | "
            f"{shipment.source} | {shipment.quantity} fish | "
            f"{shipment.density}/L"
        )

    if len(shipments) > max_shipments:
        lines.append(f"\n... and {len(shipments) - max_shipments} more")

    return "\n".join(lines)


def build_symptom_summary(observation) -> str:
    """
    Format observation symptoms for AI analysis.

    Creates readable list of observed symptoms.

    Args:
        observation: DailyObservation record

    Returns:
        Formatted symptom summary
    """
    symptoms = []

    if observation.symptoms_lethargy:
        symptoms.append("- Lethargy")
    if observation.symptoms_loss_of_appetite:
        symptoms.append("- Loss of appetite")
    if observation.symptoms_spots:
        symptoms.append("- Spots/discoloration")
    if observation.symptoms_fin_damage:
        symptoms.append("- Fin damage")
    if observation.symptoms_breathing_issues:
        symptoms.append("- Breathing issues")
    if observation.symptoms_other:
        symptoms.append(f"- Other: {observation.symptoms_other}")

    if not symptoms:
        return "No symptoms observed"

    symptom_text = "\n".join(symptoms)
    return f"""Symptoms Observed:
{symptom_text}
Overall Condition: {observation.overall_condition_score}/5"""
