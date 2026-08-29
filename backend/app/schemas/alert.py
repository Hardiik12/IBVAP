from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field, field_serializer
from app.models.enums import EventSeverity, AlertStatus


def format_utc_iso(dt: datetime) -> str:
    """Format datetime as strict ISO 8601 UTC string with Z suffix."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


class AlertUpdate(BaseModel):
    status: Optional[AlertStatus] = None
    acknowledged_by: Optional[str] = Field(None, min_length=1, max_length=36)

    class Config:
        extra = "forbid"


class AlertResponse(BaseModel):
    id: str
    event_id: str
    severity: EventSeverity
    status: AlertStatus
    message: Optional[str] = None
    created_at: datetime
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None

    @field_serializer("created_at")
    def serialize_created_at(self, dt: datetime, _info) -> str:
        return format_utc_iso(dt)

    @field_serializer("acknowledged_at")
    def serialize_acknowledged_at(self, dt: Optional[datetime], _info) -> Optional[str]:
        return format_utc_iso(dt) if dt else None

    class Config:
        from_attributes = True


DefinitionResponse = AlertResponse
