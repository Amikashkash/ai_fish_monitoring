"""
Filename: observation.py
Purpose: Daily observation model for tracking fish health during treatment
Author: Fish Monitoring System
Created: 2026-02-15

This module defines the DailyObservation ORM model for recording
daily fish health observations during the treatment period.

Dependencies:
    - sqlalchemy: ORM framework
    - app.config.database: Base class

Example:
    >>> from app.models.observation import DailyObservation
    >>> observation = DailyObservation(
    ...     treatment_id=1,
    ...     observation_date=date.today(),
    ...     overall_condition_score=4,
    ...     treatments_completed=True
    ... )
"""

from sqlalchemy import Column, Integer, String, Date, Boolean, TIMESTAMP, ForeignKey, func, CheckConstraint
from sqlalchemy.orm import relationship
from app.config.database import Base


class DailyObservation(Base):
    """
    Represents a daily health observation for fish under treatment.

    Tracks daily condition scores, symptoms, and treatment compliance
    to monitor progress and identify issues early.

    Attributes:
        id: Unique observation identifier (auto-generated)
        treatment_id: Reference to the treatment being monitored
        observation_date: Date of this observation
        overall_condition_score: General health score (1-5, where 5 is best)
        symptoms_lethargy: Whether fish show lethargy
        symptoms_loss_of_appetite: Whether fish aren't eating
        symptoms_spots: Whether fish have spots/lesions
        symptoms_fin_damage: Whether fins are damaged
        symptoms_breathing_issues: Whether fish show labored breathing
        symptoms_other: Description of any other symptoms
        treatments_completed: Whether all scheduled treatments were done
        notes: Additional observation notes
        created_at: Timestamp when observation was recorded
        treatment: Relationship to Treatment model

    Example:
        >>> observation = DailyObservation(
        ...     treatment_id=1,
        ...     observation_date=date(2026, 2, 15),
        ...     overall_condition_score=3,
        ...     symptoms_lethargy=False,
        ...     symptoms_loss_of_appetite=True,
        ...     symptoms_spots=False,
        ...     symptoms_fin_damage=False,
        ...     symptoms_breathing_issues=False,
        ...     treatments_completed=True,
        ...     notes="Some fish not eating, will monitor closely"
        ... )
    """

    __tablename__ = "daily_observations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    treatment_id = Column(Integer, ForeignKey("treatments.id", ondelete="CASCADE"), nullable=False)
    observation_date = Column(Date, nullable=False, index=True)
    overall_condition_score = Column(
        Integer,
        CheckConstraint("overall_condition_score BETWEEN 1 AND 5"),
        nullable=True
    )

    # Symptom checkboxes
    symptoms_lethargy = Column(Boolean, default=False)
    symptoms_loss_of_appetite = Column(Boolean, default=False)
    symptoms_spots = Column(Boolean, default=False)
    symptoms_fin_damage = Column(Boolean, default=False)
    symptoms_breathing_issues = Column(Boolean, default=False)
    symptoms_other = Column(String, nullable=True)

    treatments_completed = Column(Boolean, default=False)
    notes = Column(String, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    treatment = relationship("Treatment", backref="daily_observations")

    def __repr__(self) -> str:
        """String representation of observation."""
        return (
            f"<DailyObservation(id={self.id}, "
            f"treatment_id={self.treatment_id}, "
            f"date={self.observation_date}, "
            f"score={self.overall_condition_score})>"
        )

    def has_symptoms(self) -> bool:
        """
        Check if any symptoms are present.

        Returns:
            True if any symptom checkbox is checked

        Example:
            >>> observation.has_symptoms()
            True  # if any symptom is present
        """
        return any([
            self.symptoms_lethargy,
            self.symptoms_loss_of_appetite,
            self.symptoms_spots,
            self.symptoms_fin_damage,
            self.symptoms_breathing_issues,
            bool(self.symptoms_other)
        ])
