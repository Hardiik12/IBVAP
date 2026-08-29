from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, field_serializer


def format_utc_iso(dt: datetime) -> str:
    """Format datetime as strict ISO 8601 UTC string with Z suffix."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


class EvidenceBase(BaseModel):
    evidence_identifier: str = Field(..., min_length=1, max_length=50)
    file_path: str = Field(..., min_length=1, max_length=255)
    captured_at: datetime = Field(...)
    evidence_metadata: Optional[Dict[str, Any]] = Field(None, alias="metadata")

    @field_serializer("captured_at")
    def serialize_captured_at(self, dt: datetime, _info) -> str:
        return format_utc_iso(dt)

    class Config:
        populate_by_name = True


class EvidenceCreate(EvidenceBase):
    pass


class EvidenceUpdate(BaseModel):
    evidence_metadata: Optional[Dict[str, Any]] = Field(None, alias="metadata")

    class Config:
        extra = "forbid"
        populate_by_name = True


class EvidenceResponse(EvidenceBase):
    id: str
    event_id: str
    sha256_hash: Optional[str] = None
    image_url: Optional[str] = None
    created_at: datetime

    @field_serializer("created_at")
    def serialize_created_at(self, dt: datetime, _info) -> str:
        return format_utc_iso(dt)

    class Config:
        from_attributes = True
        populate_by_name = True


class EvidenceCaptureRequest(BaseModel):
    image: str = Field(..., description="Base64 encoded JPEG/PNG frame captured at the moment of intrusion")
    camera_id: Optional[str] = "cam-01"
    zone_id: Optional[str] = None
    zone_name: Optional[str] = None
    track_id: int = 1
    class_name: Optional[str] = "person"
    confidence: Optional[float] = 0.90
    bbox: Optional[List[float]] = None
    timestamp: Optional[datetime] = None


class EvidenceDetailResponse(BaseModel):
    evidence_id: str
    evidence_identifier: str
    event_id: str
    event_identifier: Optional[str] = None
    file_path: str
    sha256_hash: Optional[str] = None
    image_url: str
    captured_at: datetime
    camera_id: Optional[str] = None
    track_id: Optional[int] = None
    class_name: Optional[str] = None
    confidence: Optional[float] = None
    bbox: Optional[List[float]] = None
    severity: Optional[str] = "HIGH"
    verified_status: Optional[str] = "UNKNOWN"

    @field_serializer("captured_at")
    def serialize_captured_at(self, dt: datetime, _info) -> str:
        return format_utc_iso(dt)

    class Config:
        populate_by_name = True


class EvidenceHashResponse(BaseModel):
    id: str
    evidence_identifier: str
    sha256_hash: str
    status: str

    class Config:
        populate_by_name = True


class EvidenceVerificationResponse(BaseModel):
    evidence_id: str
    verified: bool
    status: str
    stored_hash: Optional[str] = None
    current_hash: Optional[str] = None
    verified_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_serializer("verified_at")
    def serialize_verified_at(self, dt: Optional[datetime], _info) -> Optional[str]:
        return format_utc_iso(dt) if dt else None

    class Config:
        populate_by_name = True
