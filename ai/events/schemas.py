"""Data contracts for the IBVAP intrusion event engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class EventType(str, Enum):
    """Supported security event types."""

    INTRUSION = "INTRUSION"
    LOITERING = "LOITERING"
    UNAUTHORIZED_VEHICLE = "UNAUTHORIZED_VEHICLE"


class Severity(str, Enum):
    """Alert severity levels."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class EventPayload:
    """Standardized event payload emitted upon positive state transition."""

    camera_id: str
    zone_id: str
    track_id: int
    class_name: str
    confidence: float
    bbox: list[float]  # [x1, y1, x2, y2]
    event_type: str = EventType.INTRUSION.value
    severity: str = Severity.HIGH.value
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    evidence_snapshot: str | None = None  # Base64 encoded JPEG string (optional)

    def to_dict(self) -> dict:
        """Convert event payload into a serializable dictionary matching the API contract."""
        data = {
            "camera_id": self.camera_id,
            "zone_id": self.zone_id,
            "event_type": self.event_type,
            "track_id": self.track_id,
            "class_name": self.class_name,
            "confidence": round(self.confidence, 4),
            "severity": self.severity,
            "timestamp": self.timestamp,
            "bbox": self.bbox,
        }
        if self.evidence_snapshot is not None:
            data["evidence_snapshot"] = self.evidence_snapshot
        return data
