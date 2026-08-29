"""YOLO object detector wrapper for IBVAP."""

from __future__ import annotations

import os

import numpy as np
from ultralytics import YOLO

from ai.detection.schemas import NormalizedDetection


DEFAULT_MODEL = os.getenv("YOLO_MODEL", "yolov8n.pt")
DEFAULT_CONFIDENCE = float(
    os.getenv("YOLO_CONFIDENCE", "0.35")
)


class YOLODetector:
    """Reusable YOLO detector that outputs normalized IBVAP detections."""

    def __init__(
        self,
        model_path: str = DEFAULT_MODEL,
        confidence_threshold: float = DEFAULT_CONFIDENCE,
        target_classes: set[int] | None = None,
    ) -> None:
        self.model = YOLO(model_path)
        self.confidence_threshold = confidence_threshold

        # COCO classes:
        # 0 = person
        # 2 = car
        # 3 = motorcycle
        # 5 = bus
        # 7 = truck
        self.target_classes = (
            target_classes
            if target_classes is not None
            else {0, 2, 3, 5, 7}
        )

    def detect(
        self,
        frame: np.ndarray,
    ) -> list[NormalizedDetection]:
        """
        Run object detection on one BGR frame.

        Returns normalized IBVAP detection objects.
        """

        result = self.model.predict(
            frame,
            conf=self.confidence_threshold,
            verbose=False,
        )[0]

        detections: list[NormalizedDetection] = []

        if result.boxes is None:
            return detections

        boxes = result.boxes

        for index in range(len(boxes)):

            class_id = int(boxes.cls[index].item())

            if class_id not in self.target_classes:
                continue

            confidence = float(
                boxes.conf[index].item()
            )

            x1, y1, x2, y2 = (
                boxes.xyxy[index]
                .cpu()
                .tolist()
            )

            class_name = result.names[class_id]

            detection = NormalizedDetection(
                class_id=class_id,
                class_name=class_name,
                confidence=confidence,
                bbox=[
                    float(x1),
                    float(y1),
                    float(x2),
                    float(y2),
                ],
            )

            detections.append(detection)

        return detections
