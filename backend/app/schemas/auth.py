from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field, field_serializer
from app.models.enums import UserRole


def format_utc_iso(dt: datetime) -> str:
    """Format datetime as strict ISO 8601 UTC string with Z suffix."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


class LoginRequest(BaseModel):
    username_or_email: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=1)


class CurrentUserResponse(BaseModel):
    id: str
    username: str
    email: str
    role: UserRole
    mfa_enabled: bool = False
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    @field_serializer("created_at")
    def serialize_created_at(self, dt: datetime, _info) -> str:
        return format_utc_iso(dt)

    @field_serializer("updated_at")
    def serialize_updated_at(self, dt: Optional[datetime], _info) -> Optional[str]:
        return format_utc_iso(dt) if dt else None

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    mfa_required: bool = True
    mfa_setup_required: bool = False
    mfa_token: str
    temp_token_expires_in: int = 300  # 5 minutes
    username: str
    role: UserRole


class MfaSetupResponse(BaseModel):
    secret: str
    qr_code_base64: str
    provisioning_uri: str
    username: str


class MfaVerifyRequest(BaseModel):
    mfa_token: str
    code: str = Field(..., min_length=6, max_length=6)


class MfaEnableRequest(BaseModel):
    mfa_token: str
    secret: str
    code: str = Field(..., min_length=6, max_length=6)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: CurrentUserResponse
