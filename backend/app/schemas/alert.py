from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models.enums import EventSeverity, AlertStatus


class AlertUpdate(BaseModel):
    status: Optional[AlertStatus] = None
    acknowledged_by: Optional[str] = Field(None, min_length=36, max_length=36)

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

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
DefinitionResponse = AlertResponse
