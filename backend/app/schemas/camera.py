from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models.enums import CameraSourceType


class CameraBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    camera_identifier: str = Field(..., min_length=1, max_length=50)
    source_type: CameraSourceType = Field(default=CameraSourceType.WEBCAM)
    source_url: Optional[str] = Field(None, max_length=255)
    location: Optional[str] = Field(None, max_length=100)
    is_active: bool = Field(default=True)


class CameraCreate(CameraBase):
    pass


class CameraUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    camera_identifier: Optional[str] = Field(None, min_length=1, max_length=50)
    source_type: Optional[CameraSourceType] = None
    source_url: Optional[str] = Field(None, max_length=255)
    location: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None


class CameraResponse(CameraBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
DefinitionResponse = CameraResponse
