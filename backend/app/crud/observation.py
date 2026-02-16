"""
Filename: observation.py
Purpose: CRUD operations for daily observation records
Author: Fish Monitoring System
Created: 2026-02-15

This module provides database operations for daily health observations.

Dependencies:
    - sqlalchemy.orm: Database session
    - app.models.observation: DailyObservation model
    - app.schemas.observation: Observation schemas

Example:
    >>> from app.crud import observation
    >>> new_obs = observation.create_observation(db, obs_data)
    >>> obs_list = observation.get_observations_by_treatment(db, 1)
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.models.observation import DailyObservation
from app.schemas.observation import ObservationCreate, ObservationUpdate


def create_observation(
    db: Session,
    observation: ObservationCreate
) -> DailyObservation:
    """
    Create a new daily observation.

    Args:
        db: Database session
        observation: Observation creation schema

    Returns:
        Created DailyObservation object

    Example:
        >>> obs_data = ObservationCreate(
        ...     treatment_id=1,
        ...     overall_condition_score=4,
        ...     symptoms_lethargy=False,
        ...     treatments_completed=True
        ... )
        >>> obs = create_observation(db, obs_data)
    """
    db_observation = DailyObservation(**observation.model_dump())
    db.add(db_observation)
    db.commit()
    db.refresh(db_observation)
    return db_observation


def get_observation(
    db: Session,
    observation_id: int
) -> Optional[DailyObservation]:
    """
    Get an observation by ID.

    Args:
        db: Database session
        observation_id: Observation ID

    Returns:
        DailyObservation or None

    Example:
        >>> obs = get_observation(db, 1)
    """
    return db.query(DailyObservation).filter(
        DailyObservation.id == observation_id
    ).first()


def get_observations_by_treatment(
    db: Session,
    treatment_id: int
) -> List[DailyObservation]:
    """
    Get all observations for a treatment.

    Args:
        db: Database session
        treatment_id: Treatment ID

    Returns:
        List of DailyObservation objects, ordered by date

    Example:
        >>> observations = get_observations_by_treatment(db, 1)
        >>> print(f"Total observations: {len(observations)}")
    """
    return db.query(DailyObservation).filter(
        DailyObservation.treatment_id == treatment_id
    ).order_by(DailyObservation.observation_date).all()


def get_observation_by_date(
    db: Session,
    treatment_id: int,
    observation_date: date
) -> Optional[DailyObservation]:
    """
    Get observation for a specific treatment on a specific date.

    Args:
        db: Database session
        treatment_id: Treatment ID
        observation_date: Date of observation

    Returns:
        DailyObservation or None

    Example:
        >>> today_obs = get_observation_by_date(db, 1, date.today())
    """
    return db.query(DailyObservation).filter(
        DailyObservation.treatment_id == treatment_id,
        DailyObservation.observation_date == observation_date
    ).first()


def get_observations_with_symptoms(
    db: Session,
    treatment_id: int
) -> List[DailyObservation]:
    """
    Get observations where fish showed symptoms.

    Args:
        db: Database session
        treatment_id: Treatment ID

    Returns:
        List of DailyObservation objects with symptoms

    Example:
        >>> symptomatic = get_observations_with_symptoms(db, 1)
    """
    return db.query(DailyObservation).filter(
        DailyObservation.treatment_id == treatment_id
    ).filter(
        (DailyObservation.symptoms_lethargy == True) |
        (DailyObservation.symptoms_loss_of_appetite == True) |
        (DailyObservation.symptoms_spots == True) |
        (DailyObservation.symptoms_fin_damage == True) |
        (DailyObservation.symptoms_breathing_issues == True)
    ).all()


def get_latest_observation(
    db: Session,
    treatment_id: int
) -> Optional[DailyObservation]:
    """
    Get most recent observation for a treatment.

    Args:
        db: Database session
        treatment_id: Treatment ID

    Returns:
        Latest DailyObservation or None

    Example:
        >>> latest = get_latest_observation(db, 1)
        >>> if latest:
        ...     print(f"Latest score: {latest.overall_condition_score}")
    """
    return db.query(DailyObservation).filter(
        DailyObservation.treatment_id == treatment_id
    ).order_by(DailyObservation.observation_date.desc()).first()


def update_observation(
    db: Session,
    observation_id: int,
    observation_update: ObservationUpdate
) -> Optional[DailyObservation]:
    """
    Update an existing observation.

    Args:
        db: Database session
        observation_id: Observation ID
        observation_update: Update schema

    Returns:
        Updated DailyObservation or None

    Example:
        >>> update = ObservationUpdate(
        ...     overall_condition_score=5,
        ...     notes="Significant improvement"
        ... )
        >>> updated = update_observation(db, 1, update)
    """
    db_observation = get_observation(db, observation_id)
    if not db_observation:
        return None

    update_data = observation_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_observation, field, value)

    db.commit()
    db.refresh(db_observation)
    return db_observation


def delete_observation(db: Session, observation_id: int) -> bool:
    """
    Delete an observation record.

    Args:
        db: Database session
        observation_id: Observation ID

    Returns:
        True if deleted, False if not found

    Example:
        >>> deleted = delete_observation(db, 1)
    """
    db_observation = get_observation(db, observation_id)
    if not db_observation:
        return False

    db.delete(db_observation)
    db.commit()
    return True


def count_observations(db: Session, treatment_id: int) -> int:
    """
    Count observations for a treatment.

    Args:
        db: Database session
        treatment_id: Treatment ID

    Returns:
        Number of observations

    Example:
        >>> count = count_observations(db, 1)
    """
    return db.query(DailyObservation).filter(
        DailyObservation.treatment_id == treatment_id
    ).count()
