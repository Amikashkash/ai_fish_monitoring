"""
Filename: ai_knowledge.py
Purpose: CRUD operations for AI knowledge base records
Author: Fish Monitoring System
Created: 2026-02-15

This module provides database operations for AI-learned knowledge patterns.

Dependencies:
    - sqlalchemy.orm: Database session
    - app.models.ai_knowledge: AIKnowledge model

Example:
    >>> from app.crud import ai_knowledge
    >>> knowledge = ai_knowledge.get_knowledge_for_fish_source(
    ...     db, "Betta splendens", "Thailand"
    ... )
"""

from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from app.models.ai_knowledge import AIKnowledge


def create_or_update_knowledge(
    db: Session,
    source_country: str,
    scientific_name: str,
    successful_protocols: Optional[Dict[str, Any]] = None,
    success_rate: Optional[float] = None,
    sample_size: int = 0,
    insights: Optional[str] = None
) -> AIKnowledge:
    """
    Create or update AI knowledge for a fish/source combination.

    If knowledge exists, updates it. Otherwise, creates new record.

    Args:
        db: Database session
        source_country: Source country name
        scientific_name: Fish species scientific name
        successful_protocols: JSON of successful drug protocols
        success_rate: Average success rate percentage
        sample_size: Number of shipments this is based on
        insights: AI-generated insights text

    Returns:
        Created or updated AIKnowledge object

    Example:
        >>> knowledge = create_or_update_knowledge(
        ...     db,
        ...     source_country="Thailand",
        ...     scientific_name="Betta splendens",
        ...     successful_protocols={"drugs": ["Methylene Blue"]},
        ...     success_rate=92.5,
        ...     sample_size=10,
        ...     insights="High success rate with standard protocol"
        ... )
    """
    # Try to get existing knowledge
    existing = get_knowledge_for_fish_source(db, scientific_name, source_country)

    if existing:
        # Update existing
        existing.successful_protocols = successful_protocols
        existing.success_rate = success_rate
        existing.sample_size = sample_size
        existing.insights = insights
        db.commit()
        db.refresh(existing)
        return existing
    else:
        # Create new
        new_knowledge = AIKnowledge(
            source_country=source_country,
            scientific_name=scientific_name,
            successful_protocols=successful_protocols,
            success_rate=success_rate,
            sample_size=sample_size,
            insights=insights
        )
        db.add(new_knowledge)
        db.commit()
        db.refresh(new_knowledge)
        return new_knowledge


def get_knowledge_for_fish_source(
    db: Session,
    scientific_name: str,
    source_country: str
) -> Optional[AIKnowledge]:
    """
    Get AI knowledge for a specific fish/source combination.

    Args:
        db: Database session
        scientific_name: Fish species scientific name
        source_country: Source country

    Returns:
        AIKnowledge object or None

    Example:
        >>> knowledge = get_knowledge_for_fish_source(
        ...     db, "Betta splendens", "Thailand"
        ... )
        >>> if knowledge:
        ...     print(f"Success rate: {knowledge.success_rate}%")
        ...     print(f"Based on {knowledge.sample_size} shipments")
    """
    return db.query(AIKnowledge).filter(
        AIKnowledge.scientific_name == scientific_name,
        AIKnowledge.source_country == source_country
    ).first()


def get_all_knowledge_for_species(
    db: Session,
    scientific_name: str
) -> List[AIKnowledge]:
    """
    Get all AI knowledge entries for a fish species (all sources).

    Args:
        db: Database session
        scientific_name: Fish species scientific name

    Returns:
        List of AIKnowledge objects

    Example:
        >>> all_betta_knowledge = get_all_knowledge_for_species(
        ...     db, "Betta splendens"
        ... )
        >>> for k in all_betta_knowledge:
        ...     print(f"{k.source_country}: {k.success_rate}%")
    """
    return db.query(AIKnowledge).filter(
        AIKnowledge.scientific_name == scientific_name
    ).all()


def get_all_knowledge_for_source(
    db: Session,
    source_country: str
) -> List[AIKnowledge]:
    """
    Get all AI knowledge for a source country (all species).

    Args:
        db: Database session
        source_country: Source country

    Returns:
        List of AIKnowledge objects

    Example:
        >>> thailand_knowledge = get_all_knowledge_for_source(db, "Thailand")
    """
    return db.query(AIKnowledge).filter(
        AIKnowledge.source_country == source_country
    ).all()


def get_all_knowledge(db: Session) -> List[AIKnowledge]:
    """
    Get all AI knowledge entries.

    Args:
        db: Database session

    Returns:
        List of all AIKnowledge objects

    Example:
        >>> all_knowledge = get_all_knowledge(db)
        >>> print(f"Total knowledge entries: {len(all_knowledge)}")
    """
    return db.query(AIKnowledge).all()


def get_high_confidence_knowledge(
    db: Session,
    min_sample_size: int = 5,
    min_success_rate: float = 85.0
) -> List[AIKnowledge]:
    """
    Get knowledge entries with high confidence (sufficient data and success).

    Args:
        db: Database session
        min_sample_size: Minimum number of shipments (default 5)
        min_success_rate: Minimum success rate percentage (default 85%)

    Returns:
        List of high-confidence AIKnowledge objects

    Example:
        >>> reliable = get_high_confidence_knowledge(db)
        >>> for k in reliable:
        ...     print(f"{k.scientific_name} from {k.source_country}")
    """
    return db.query(AIKnowledge).filter(
        AIKnowledge.sample_size >= min_sample_size,
        AIKnowledge.success_rate >= min_success_rate
    ).all()


def increment_sample_size(
    db: Session,
    scientific_name: str,
    source_country: str
) -> Optional[AIKnowledge]:
    """
    Increment sample size for a knowledge entry.

    Args:
        db: Database session
        scientific_name: Fish species
        source_country: Source country

    Returns:
        Updated AIKnowledge or None

    Example:
        >>> knowledge = increment_sample_size(db, "Betta splendens", "Thailand")
    """
    knowledge = get_knowledge_for_fish_source(db, scientific_name, source_country)
    if not knowledge:
        return None

    knowledge.sample_size += 1
    db.commit()
    db.refresh(knowledge)
    return knowledge


def delete_knowledge(
    db: Session,
    knowledge_id: int
) -> bool:
    """
    Delete an AI knowledge entry.

    Args:
        db: Database session
        knowledge_id: Knowledge ID

    Returns:
        True if deleted, False if not found

    Example:
        >>> deleted = delete_knowledge(db, 1)
    """
    knowledge = db.query(AIKnowledge).filter(
        AIKnowledge.id == knowledge_id
    ).first()

    if not knowledge:
        return False

    db.delete(knowledge)
    db.commit()
    return True


def count_knowledge_entries(db: Session) -> int:
    """
    Count total AI knowledge entries.

    Args:
        db: Database session

    Returns:
        Number of knowledge entries

    Example:
        >>> total = count_knowledge_entries(db)
    """
    return db.query(AIKnowledge).count()


def get_best_source_for_species(
    db: Session,
    scientific_name: str
) -> Optional[AIKnowledge]:
    """
    Get the best source (highest success rate) for a fish species.

    Args:
        db: Database session
        scientific_name: Fish species scientific name

    Returns:
        AIKnowledge with highest success rate or None

    Example:
        >>> best = get_best_source_for_species(db, "Betta splendens")
        >>> if best:
        ...     print(f"Best source: {best.source_country}")
    """
    return db.query(AIKnowledge).filter(
        AIKnowledge.scientific_name == scientific_name
    ).order_by(AIKnowledge.success_rate.desc()).first()
