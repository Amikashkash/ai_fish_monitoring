"""
Filename: shipment.py
Purpose: Shipment database model for tracking fish arrivals
Author: Fish Monitoring System
Created: 2026-02-15

This module defines the Shipment ORM model for storing fish shipment records.
Each shipment represents a batch of fish received from a supplier.

Dependencies:
    - sqlalchemy: ORM framework
    - app.config.database: Base class

Example:
    >>> from app.models.shipment import Shipment
    >>> shipment = Shipment(
    ...     scientific_name="Betta splendens",
    ...     common_name="Siamese Fighting Fish",
    ...     source="Thailand",
    ...     quantity=50,
    ...     aquarium_volume_liters=200
    ... )
"""

from sqlalchemy import Column, Integer, String, Date, DECIMAL, TIMESTAMP, func, Computed
from app.config.database import Base


class Shipment(Base):
    """
    Represents a fish shipment record.

    Stores details about each batch of fish received from suppliers,
    including species information, source, quantity, tank conditions,
    and pricing.

    Attributes:
        id: Unique shipment identifier (auto-generated)
        date: Date shipment was received
        scientific_name: Latin/scientific name of the fish species
        common_name: Common/trade name of the fish
        source: Country or supplier source
        quantity: Number of fish in the shipment
        fish_size: Size description (small/medium/large or measurements)
        aquarium_volume_liters: Tank volume in liters for density calculation
        density: Auto-calculated fish per liter ratio
        price_per_fish: Individual fish price (optional)
        total_price: Total shipment cost (optional)
        created_at: Timestamp when record was created

    Example:
        >>> shipment = Shipment(
        ...     date=date.today(),
        ...     scientific_name="Paracheirodon innesi",
        ...     common_name="Neon Tetra",
        ...     source="Singapore",
        ...     quantity=100,
        ...     fish_size="small",
        ...     aquarium_volume_liters=500,
        ...     price_per_fish=0.50,
        ...     total_price=50.00
        ... )
    """

    __tablename__ = "shipments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    date = Column(Date, nullable=False)
    scientific_name = Column(String, nullable=False, index=True)
    common_name = Column(String, nullable=False)
    source = Column(String, nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    fish_size = Column(String, nullable=True)
    aquarium_volume_liters = Column(Integer, nullable=False)
    # Computed column: density = quantity / volume
    density = Column(
        DECIMAL(10, 2),
        Computed("quantity::DECIMAL / aquarium_volume_liters")
    )
    price_per_fish = Column(DECIMAL(10, 2), nullable=True)
    total_price = Column(DECIMAL(10, 2), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    def __repr__(self) -> str:
        """String representation of shipment."""
        return (
            f"<Shipment(id={self.id}, "
            f"species='{self.scientific_name}', "
            f"source='{self.source}', "
            f"quantity={self.quantity})>"
        )
