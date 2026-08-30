import hashlib
import logging
import os
from typing import Optional

import numpy as np

try:
    from ultralytics import YOLO
except ImportError:
    YOLO = None  # type: ignore

from ai.detection.schemas import NormalizedDetection
from ai.core.config import ai_settings

logger = logging.getLogger(__name__)

DEFAULT_MODEL = os.getenv("YOLO_MODEL", "yolov8n.pt")
DEFAULT_CONFIDENCE = float(os.getenv("YOLO_CONFIDENCE", "0.35"))


def compute_file_sha256(file_path: str) -> str:
    """Computes SHA-256 hash of a local model file in 64KB chunks."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            sha256.update(chunk)
    return sha256.hexdigest().lower()


class YOLODetector:
    """Reusable YOLO detector that outputs normalized IBVAP detections."""

    def __init__(
        self,
        model_path: str = DEFAULT_MODEL,
        confidence_threshold: float = DEFAULT_CONFIDENCE,
        target_classes: set[int] | None = None,
        expected_sha256: Optional[str] = None,
    ) -> None:
        if YOLO is None:
            raise RuntimeError("Ultralytics package is not installed.")

        self.model = YOLO(model_path)
        self.confidence_threshold = confidence_threshold

        # Verify model file integrity if expected SHA-256 is configured
        sha_to_check = expected_sha256 or ai_settings.MODEL_SHA256
        if sha_to_check:
            weights_file = getattr(self.model, "ckpt_path", model_path)
            if not os.path.isfile(str(weights_file)):
                weights_file = model_path
            if os.path.isfile(str(weights_file)):
                actual_sha = compute_file_sha256(str(weights_file))
                if actual_sha.lower() != sha_to_check.lower():
                    err_msg = (
                        f"Model integrity verification failed for '{weights_file}'. "
                        f"Expected SHA-256: {sha_to_check}, got: {actual_sha}."
                    )
                    logger.error(err_msg)
                    raise RuntimeError(err_msg)
                logger.info(f"Model integrity verified successfully for '{weights_file}'.")
            else:
                err_msg = f"Model file '{model_path}' not found for integrity verification."
                logger.error(err_msg)
                raise RuntimeError(err_msg)



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
