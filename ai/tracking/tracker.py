"""ByteTrack multi-object tracker integration for IBVAP."""

from __future__ import annotations

import os

import numpy as np
from ultralytics import YOLO

from ai.tracking.schemas import Track

DEFAULT_MODEL = os.getenv("YOLO_MODEL", "yolov8n.pt")
DEFAULT_TRACKER = os.getenv("TRACKER_CONFIG", "bytetrack.yaml")
DEFAULT_CONFIDENCE = float(os.getenv("YOLO_CONFIDENCE", "0.35"))


class ByteTracker:
    """Multi-object tracker using Ultralytics YOLO with ByteTrack."""

    def __init__(
        self,
        model_path: str = DEFAULT_MODEL,
        tracker_config: str = DEFAULT_TRACKER,
        confidence_threshold: float = DEFAULT_CONFIDENCE,
        target_classes: set[int] | None = None,
    ) -> None:
        self.model = YOLO(model_path)
        self.tracker_config = tracker_config
        self.confidence_threshold = confidence_threshold

        # Target classes (default COCO: 0=person, 2=car, 3=motorcycle, 5=bus, 7=truck)
        self.target_classes = (
            target_classes
            if target_classes is not None
            else {0, 2, 3, 5, 7}
        )

    def track(
        self,
        frame: np.ndarray,
        persist: bool = True,
    ) -> list[Track]:
        """
        Run object detection & multi-object tracking on a single frame.

        Returns a list of standardized Track objects with persistent track IDs.
        """
        results = self.model.track(
            frame,
            persist=persist,
            tracker=self.tracker_config,
            conf=self.confidence_threshold,
            verbose=False,
        )

        tracks: list[Track] = []
        if not results:
            return tracks

        result = results[0]
        if result.boxes is None:
            return tracks

        boxes = result.boxes
        has_ids = boxes.id is not None

        for index in range(len(boxes)):
            class_id = int(boxes.cls[index].item())

            if class_id not in self.target_classes:
                continue

            # If the tracker assigned an ID, use it; otherwise assign -1
            if has_ids and boxes.id is not None:
                track_id = int(boxes.id[index].item())
            else:
                track_id = -1

            confidence = float(boxes.conf[index].item())
            x1, y1, x2, y2 = boxes.xyxy[index].cpu().tolist()
            class_name = result.names[class_id]

            track = Track(
                track_id=track_id,
                class_id=class_id,
                class_name=class_name,
                confidence=confidence,
                bbox=[float(x1), float(y1), float(x2), float(y2)],
            )
            tracks.append(track)

        return tracks

    def reset(self) -> None:
        """Reset tracking state across video source changes."""
        if hasattr(self.model, "predictor") and self.model.predictor is not None:
            if hasattr(self.model.predictor, "trackers"):
                self.model.predictor.trackers = None
