"""Data contracts for the IBVAP detection module."""

from dataclasses import dataclass


@dataclass
class NormalizedDetection:
    """Standard object detection representation used inside IBVAP."""

    class_id: int
    class_name: str
    confidence: float
    bbox: list[float]

    def to_dict(self) -> dict:
        """Convert the detection into a serializable dictionary."""
        return {
            "class_id": self.class_id,
            "class_name": self.class_name,
            "confidence": self.confidence,
            "bbox": self.bbox,
        }
