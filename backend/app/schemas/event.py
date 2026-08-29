from datetime import datetime, timezone
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator, field_serializer
from app.models.enums import EventType, EventSeverity, EventStatus


def format_utc_iso(dt: datetime) -> str:
    """Format datetime as strict ISO 8601 UTC string with Z suffix."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


class EventBase(BaseModel):
    event_identifier: str = Field(..., min_length=1, max_length=50)
    event_type: EventType = Field(default=EventType.INTRUSION)
    camera_id: str = Field(..., min_length=1, max_length=36)
    zone_id: Optional[str] = Field(None, min_length=1, max_length=36)
    track_id: int = Field(...)
    timestamp: datetime = Field(...)
    severity: EventSeverity = Field(default=EventSeverity.HIGH)
    status: EventStatus = Field(default=EventStatus.NEW)
    bounding_box: Optional[Dict[str, Any]] = None
    position: Optional[Dict[str, Any]] = None
    event_metadata: Optional[Dict[str, Any]] = Field(None, alias="metadata")

    @field_serializer("timestamp")
    def serialize_timestamp(self, dt: datetime, _info) -> str:
        return format_utc_iso(dt)

    @field_validator("bounding_box")
    @classmethod
    def validate_bounding_box(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if v is None:
            return v
        if not isinstance(v, dict):
            raise ValueError("Bounding box must be a JSON dictionary object")
        required_keys = {"x1", "y1", "x2", "y2"}
        if not required_keys.issubset(v.keys()):
            raise ValueError("Bounding box must contain keys: x1, y1, x2, y2")
        for key in required_keys:
            if not isinstance(v[key], (int, float)):
                raise ValueError(f"Bounding box coordinate '{key}' must be a numeric value")
        return v

    @field_validator("position")
    @classmethod
    def validate_position(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if v is None:
            return v
        if not isinstance(v, dict):
            raise ValueError("Position must be a JSON dictionary object")
        required_keys = {"x", "y"}
        if not required_keys.issubset(v.keys()):
            raise ValueError("Position must contain keys: x, y")
        for key in required_keys:
            if not isinstance(v[key], (int, float)):
                raise ValueError(f"Position coordinate '{key}' must be a numeric value")
        return v

    class Config:
        populate_by_name = True


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    status: Optional[EventStatus] = None
    severity: Optional[EventSeverity] = None
    event_metadata: Optional[Dict[str, Any]] = Field(None, alias="metadata")

    class Config:
        extra = "forbid"
        populate_by_name = True


class EventResponse(EventBase):
    id: str
    created_at: datetime
    alert_id: Optional[str] = None

    @field_serializer("created_at")
    def serialize_created_at(self, dt: datetime, _info) -> str:
        return format_utc_iso(dt)

    class Config:
        from_attributes = True
        populate_by_name = True


DefinitionResponse = EventResponse
