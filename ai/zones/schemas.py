"""Data contracts for the IBVAP virtual polygon zones module."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ZoneState(str, Enum):
    """Zone occupancy state."""

    INSIDE = "INSIDE"
    OUTSIDE = "OUTSIDE"


@dataclass
class ZoneConfig:
    """Configuration schema for a virtual restricted polygon zone."""

    zone_id: str
    name: str
    polygon_coordinates: list[list[float]]  # [[x1, y1], [x2, y2], ...]
    is_normalized: bool = False  # True if coordinates are in [0.0, 1.0] range
    camera_id: str = "default_cam"
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert zone configuration into a serializable dictionary."""
        return {
            "zone_id": self.zone_id,
            "name": self.name,
            "polygon_coordinates": self.polygon_coordinates,
            "is_normalized": self.is_normalized,
            "camera_id": self.camera_id,
            "metadata": self.metadata,
        }
