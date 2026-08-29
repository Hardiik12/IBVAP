from typing import List, Optional
from pydantic import BaseModel, Field


class ZonePolygonInput(BaseModel):
    id: str
    name: Optional[str] = None
    polygon: List[List[float]] = Field(..., description="Normalized polygon coordinates [[x, y], ...]")


class DetectionRequest(BaseModel):
    image: str = Field(..., description="Base64 encoded JPEG/PNG image or data URL")
    camera_id: Optional[str] = "cam-01"
    confidence_threshold: Optional[float] = 0.30
    zones: Optional[List[ZonePolygonInput]] = None
    detect_all_classes: Optional[bool] = False


class NormalizedDetectionItem(BaseModel):
    track_id: int
    class_id: int
    class_name: str
    confidence: float
    bbox: List[float] = Field(..., description="Normalized bounding box [x1, y1, x2, y2] in range 0.0-1.0")
    reference_point: List[float] = Field(..., description="Normalized bottom-center reference point [x_center, y_bottom]")
    is_inside_zone: bool = False
    zone_id: Optional[str] = None
    zone_name: Optional[str] = None


class DetectionResponse(BaseModel):
    detections: List[NormalizedDetectionItem]
    inference_ms: float
    frame_width: int
    frame_height: int
    total_objects: int
