"""
Filename: followup.py
Purpose: Follow-up assessment model for post-treatment evaluation
Author: Fish Monitoring System
Created: 2026-02-15

This module defines the FollowupAssessment ORM model for 5-day
post-treatment evaluations that feed into AI learning.

Dependencies:
    - sqlalchemy: ORM framework
    - app.config.database: Base class

Example:
    >>> from app.models.followup import FollowupAssessment
    >>> followup = FollowupAssessment(
    ...     treatment_id=1,
    ...     followup_date=date.today(),
    ...     stability_score=5,
    ...     symptoms_returned=False,
    ...     survival_count=48,
    ...     success_rate=96.0
    ... )
"""

from sqlalchemy import Column, Integer, String, Date, Boolean, DECIMAL, TIMESTAMP, ForeignKey, func, CheckConstraint
from sqlalchemy.orm import relationship
from app.config.database import Base


class FollowupAssessment(Base):
    """
    Represents a 5-day post-treatment assessment.

    This assessment is critical for AI learning, as it determines
    whether a treatment protocol was successful and should be
    recommended for future shipments.

    Attributes:
        id: Unique assessment identifier (auto-generated)
        treatment_id: Reference to the completed treatment
        followup_date: Date of follow-up (typically treatment_end + 5 days)
        stability_score: Fish stability score (1-5, where 5 is best)
        symptoms_returned: Whether symptoms came back after treatment
        returned_symptoms: Description of returned symptoms (if any)
        survival_count: Number of fish that survived
        success_rate: Percentage of fish that survived (0-100)
        recommendation: Suggested protocol adjustments for future
        ai_learning_notes: AI-generated insights from this outcome
        created_at: Timestamp when assessment was recorded
        treatment: Relationship to Treatment model

    Example:
        >>> followup = FollowupAssessment(
        ...     treatment_id=1,
        ...     followup_date=date(2026, 2, 20),
        ...     stability_score=4,
        ...     symptoms_returned=False,
        ...     survival_count=47,
        ...     success_rate=94.0,
        ...     recommendation="Protocol effective, maintain for future",
        ...     ai_learning_notes="High success rate, add to knowledge base"
        ... )
    """

    __tablename__ = "followup_assessments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    treatment_id = Column(Integer, ForeignKey("treatments.id", ondelete="CASCADE"), nullable=False)
    followup_date = Column(Date, nullable=False)
    stability_score = Column(
        Integer,
        CheckConstraint("stability_score BETWEEN 1 AND 5"),
        nullable=True
    )
    symptoms_returned = Column(Boolean, default=False)
    returned_symptoms = Column(String, nullable=True)
    survival_count = Column(Integer, nullable=True)
    success_rate = Column(DECIMAL(5, 2), nullable=True)  # Percentage (0-100)
    recommendation = Column(String, nullable=True)
    ai_learning_notes = Column(String, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    treatment = relationship("Treatment", backref="followup_assessments")

    def __repr__(self) -> str:
        """String representation of followup assessment."""
        return (
            f"<FollowupAssessment(id={self.id}, "
            f"treatment_id={self.treatment_id}, "
            f"success_rate={self.success_rate}%)>"
        )

    def is_successful(self, threshold: float = 80.0) -> bool:
        """
        Determine if treatment was successful based on success rate.

        Args:
            threshold: Minimum success rate to consider successful (default 80%)

        Returns:
            True if success_rate >= threshold

        Example:
            >>> followup.success_rate = 85.5
            >>> followup.is_successful()
            True
            >>> followup.is_successful(threshold=90.0)
            False
        """
        if self.success_rate is None:
            return False
        return float(self.success_rate) >= threshold
