from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.schemas.event import EventResponse
from app.schemas.alert import AlertResponse


class WebSocketEventMessage(BaseModel):
    type: str
    timestamp: datetime
    event: EventResponse
    alert: Optional[AlertResponse] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
