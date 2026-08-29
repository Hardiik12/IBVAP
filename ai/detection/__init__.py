"""IBVAP object detection module."""

from ai.detection.detector import YOLODetector
from ai.detection.schemas import NormalizedDetection

__all__ = [
    "YOLODetector",
    "NormalizedDetection",
]
