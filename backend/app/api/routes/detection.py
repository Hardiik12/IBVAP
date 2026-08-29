import base64
import time
import logging
from typing import Optional, Tuple
import cv2
import numpy as np
from fastapi import APIRouter, HTTPException, status

from app.schemas.detection import (
    DetectionRequest,
    DetectionResponse,
    NormalizedDetectionItem,
    ZonePolygonInput,
)

logger = logging.getLogger(__name__)

router = APIRouter()

# Singleton tracker instances
_tracker_instance = None
_detector_instance = None


def get_ai_tracker():
    """Lazy load singleton tracker to keep YOLOv8 model weights warm in RAM."""
    global _tracker_instance
    if _tracker_instance is None:
        try:
            from ai.tracking.tracker import ByteTracker
            _tracker_instance = ByteTracker(
                model_path="yolov8n.pt",
                confidence_threshold=0.25,
                target_classes=None,  # Detect all relevant objects (person, phones, laptops, bottles, vehicles, etc.)
            )
            logger.info("Initialized shared ByteTracker instance with YOLOv8n.")
        except Exception as e:
            logger.error(f"Failed to initialize ByteTracker: {e}")
            raise e
    return _tracker_instance


def decode_base64_image(image_data: str) -> Tuple[np.ndarray, int, int]:
    """Decode base64 string or data URL to OpenCV BGR numpy array."""
    try:
        if "," in image_data:
            image_data = image_data.split(",", 1)[1]

        image_bytes = base64.b64decode(image_data)
        np_arr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if frame is None or frame.size == 0:
            raise ValueError("Decoded frame is empty or invalid format.")

        height, width = frame.shape[:2]
        return frame, width, height
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid base64 image data: {e}",
        )


def check_point_in_normalized_polygon(
    point: Tuple[float, float],
    polygon: list[list[float]],
) -> bool:
    """Evaluate point-in-polygon containment using OpenCV pointPolygonTest."""
    if len(polygon) < 3:
        return False
    poly_np = np.array(polygon, dtype=np.float32)
    pt_x, pt_y = point
    result = cv2.pointPolygonTest(poly_np, (float(pt_x), float(pt_y)), measureDist=False)
    return result >= 0


@router.post("/detect", response_model=DetectionResponse)
def detect_frame(request: DetectionRequest) -> DetectionResponse:
    """
    Real-time AI Frame Inference Endpoint.
    Accepts browser webcam frame (Base64 JPEG), runs YOLOv8 + ByteTrack,
    evaluates zone containment, and returns normalized detections.
    """
    t0 = time.perf_counter()

    # 1. Decode frame
    frame, width, height = decode_base64_image(request.image)

    # 2. Run tracker / detector
    tracker = get_ai_tracker()
    
    # Optionally adjust confidence threshold
    if request.confidence_threshold:
        tracker.confidence_threshold = request.confidence_threshold

    tracks = tracker.track(frame)

    # Default fallback zone if none supplied: standard perimeter zone
    active_zones = request.zones or [
        ZonePolygonInput(
            id="zone-alpha",
            name="Perimeter Restricted Sector",
            polygon=[[0.2, 0.25], [0.8, 0.25], [0.85, 0.85], [0.15, 0.85]],
        )
    ]

    normalized_items: list[NormalizedDetectionItem] = []

    for track in tracks:
        x1, y1, x2, y2 = track.bbox

        # Normalize bounding box coordinates to 0.0 - 1.0 range
        norm_x1 = max(0.0, min(1.0, float(x1) / width))
        norm_y1 = max(0.0, min(1.0, float(y1) / height))
        norm_x2 = max(0.0, min(1.0, float(x2) / width))
        norm_y2 = max(0.0, min(1.0, float(y2) / height))

        # Reference point: bottom-center where subject touches ground
        norm_ref_x = (norm_x1 + norm_x2) / 2.0
        norm_ref_y = norm_y2

        # Check zone containment
        is_inside = False
        matched_zone_id: Optional[str] = None
        matched_zone_name: Optional[str] = None

        for z in active_zones:
            if check_point_in_normalized_polygon((norm_ref_x, norm_ref_y), z.polygon):
                is_inside = True
                matched_zone_id = z.id
                matched_zone_name = z.name
                break

        normalized_items.append(
            NormalizedDetectionItem(
                track_id=track.track_id if track.track_id > 0 else 1,
                class_id=track.class_id,
                class_name=track.class_name,
                confidence=round(track.confidence, 2),
                bbox=[norm_x1, norm_y1, norm_x2, norm_y2],
                reference_point=[norm_ref_x, norm_ref_y],
                is_inside_zone=is_inside,
                zone_id=matched_zone_id,
                zone_name=matched_zone_name,
            )
        )

    t1 = time.perf_counter()
    inference_ms = round((t1 - t0) * 1000.0, 2)

    return DetectionResponse(
        detections=normalized_items,
        inference_ms=inference_ms,
        frame_width=width,
        frame_height=height,
        total_objects=len(normalized_items),
    )
