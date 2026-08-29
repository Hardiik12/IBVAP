"""Data contracts for the IBVAP tracking module."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Track:
    """Standard multi-object track representation used inside IBVAP."""

    track_id: int
    class_id: int
    class_name: str
    confidence: float
    bbox: list[float]  # [x1, y1, x2, y2]
    reference_point: tuple[float, float] = field(default=(0.0, 0.0))
    current_zone_state: str = "OUTSIDE"
    last_updated: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def __post_init__(self) -> None:
        if self.reference_point == (0.0, 0.0) and len(self.bbox) == 4:
            x1, _y1, x2, y2 = self.bbox
            self.reference_point = ((x1 + x2) / 2.0, float(y2))

    def to_dict(self) -> dict:
        """Convert track into a serializable dictionary."""
        return {
            "track_id": self.track_id,
            "class_id": self.class_id,
            "class_name": self.class_name,
            "confidence": self.confidence,
            "bbox": self.bbox,
            "reference_point": list(self.reference_point),
            "current_zone_state": self.current_zone_state,
            "last_updated": self.last_updated,
        }
