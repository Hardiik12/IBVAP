from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from app.models.enums import ZoneType


class ZoneBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    zone_type: ZoneType = Field(default=ZoneType.RESTRICTED)
    polygon_coordinates: List[List[float]] = Field(..., alias="polygon")
    is_active: bool = Field(default=True)

    @field_validator("polygon_coordinates")
    @classmethod
    def validate_polygon(cls, v: List[List[float]]) -> List[List[float]]:
        if not isinstance(v, list):
            raise ValueError("Polygon coordinates must be a list")
        if len(v) < 3:
            raise ValueError("Polygon must contain at least 3 points to form a closed shape")
        for idx, point in enumerate(v):
            if not isinstance(point, list) and not isinstance(point, tuple):
                raise ValueError(f"Point at index {idx} must be a list or tuple of coordinates")
            if len(point) != 2:
                raise ValueError(f"Point at index {idx} must contain exactly two values [x, y]")
            x, y = point
            if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
                raise ValueError(f"Coordinates at index {idx} must be numeric")
            if not (0.0 <= x <= 1.0) or not (0.0 <= y <= 1.0):
                raise ValueError(f"Coordinates at index {idx} ({x}, {y}) must be normalized between 0.0 and 1.0")
        return v

    class Config:
        populate_by_name = True


class ZoneCreate(ZoneBase):
    pass


class ZoneUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    zone_type: Optional[ZoneType] = None
    polygon_coordinates: Optional[List[List[float]]] = Field(None, alias="polygon")
    is_active: Optional[bool] = None

    @field_validator("polygon_coordinates")
    @classmethod
    def validate_polygon_optional(cls, v: Optional[List[List[float]]]) -> Optional[List[List[float]]]:
        if v is None:
            return v
        return ZoneBase.validate_polygon(v)

    class Config:
        populate_by_name = True


class ZoneResponse(ZoneBase):
    id: str
    camera_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
DefinitionResponse = ZoneResponse
