from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class EvidenceBase(BaseModel):
    evidence_identifier: str = Field(..., min_length=1, max_length=50)
    file_path: str = Field(..., min_length=1, max_length=255)
    captured_at: datetime = Field(...)
    evidence_metadata: Optional[Dict[str, Any]] = Field(None, alias="metadata")

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
    created_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


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

    class Config:
        populate_by_name = True
