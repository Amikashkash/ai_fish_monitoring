"""
Filename: ai_knowledge.py
Purpose: AI knowledge base model for learned treatment patterns
Author: Fish Monitoring System
Created: 2026-02-15

This module defines the AIKnowledge ORM model for storing learned
patterns and successful protocols discovered from historical data.

Dependencies:
    - sqlalchemy: ORM framework
    - app.config.database: Base class

Example:
    >>> from app.models.ai_knowledge import AIKnowledge
    >>> knowledge = AIKnowledge(
    ...     source_country="Thailand",
    ...     scientific_name="Betta splendens",
    ...     success_rate=92.5,
    ...     sample_size=10
    ... )
"""

from sqlalchemy import Column, Integer, String, DECIMAL, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import JSONB
from app.config.database import Base


class AIKnowledge(Base):
    """
    Represents accumulated AI knowledge about fish/source combinations.

    This table stores learned patterns from historical treatments,
    enabling the AI to make data-driven recommendations for future
    shipments of the same fish species from the same source.

    Attributes:
        id: Unique knowledge record identifier (auto-generated)
        source_country: Source country for this knowledge
        scientific_name: Fish species this knowledge applies to
        successful_protocols: JSON array of successful drug combinations
        success_rate: Average success rate percentage for this combination
        sample_size: Number of shipments this knowledge is based on
        last_updated: Timestamp when knowledge was last updated
        insights: AI-generated insights and patterns

    Unique Constraint:
        (source_country, scientific_name) - one record per fish/source combo

    Example:
        >>> knowledge = AIKnowledge(
        ...     source_country="Sri Lanka",
        ...     scientific_name="Pterophyllum scalare",
        ...     successful_protocols='{"drugs": ["Methylene Blue", "Salt"], "dosage": [2.0, 1.0]}',
        ...     success_rate=88.5,
        ...     sample_size=8,
        ...     insights="High density shipments require extended treatment"
        ... )
    """

    __tablename__ = "ai_knowledge"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    source_country = Column(String, nullable=False, index=True)
    scientific_name = Column(String, nullable=False, index=True)
    successful_protocols = Column(JSONB, nullable=True)  # PostgreSQL JSON column
    success_rate = Column(DECIMAL(5, 2), nullable=True)  # Percentage (0-100)
    sample_size = Column(Integer, nullable=True, default=0)
    last_updated = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    insights = Column(String, nullable=True)

    # Unique constraint on combination
    __table_args__ = (
        {"schema": None},  # Use default schema
    )

    def __repr__(self) -> str:
        """String representation of AI knowledge."""
        return (
            f"<AIKnowledge(id={self.id}, "
            f"source='{self.source_country}', "
            f"species='{self.scientific_name}', "
            f"success_rate={self.success_rate}%, "
            f"n={self.sample_size})>"
        )

    def has_sufficient_data(self, min_sample_size: int = 3) -> bool:
        """
        Check if there's enough data for reliable recommendations.

        Args:
            min_sample_size: Minimum number of samples needed (default 3)

        Returns:
            True if sample_size >= min_sample_size

        Example:
            >>> knowledge.sample_size = 5
            >>> knowledge.has_sufficient_data()
            True
            >>> knowledge.has_sufficient_data(min_sample_size=10)
            False
        """
        if self.sample_size is None:
            return False
        return self.sample_size >= min_sample_size

    def get_confidence_level(self) -> str:
        """
        Determine confidence level based on sample size and success rate.

        Returns:
            "high", "medium", "low", or "no_data"

        Example:
            >>> knowledge.sample_size = 10
            >>> knowledge.success_rate = 90.0
            >>> knowledge.get_confidence_level()
            'high'
        """
        if self.sample_size is None or self.sample_size == 0:
            return "no_data"

        if self.sample_size >= 5 and self.success_rate >= 85:
            return "high"
        elif self.sample_size >= 3 and self.success_rate >= 70:
            return "medium"
        else:
            return "low"
