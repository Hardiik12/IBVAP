from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from app.models.user import UserRole


class LoginRequest(BaseModel):
    username_or_email: str
    password: str


class CurrentUserResponse(BaseModel):
    id: str
    username: str
    email: str
    role: UserRole
    mfa_enabled: bool
    face_enrolled: bool
    face_enrolled_at: Optional[datetime] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    face_verification_required: bool = True
    face_enrolled: bool = False
    temp_token: str
    temp_token_expires_in: int = 300
    username: str
    role: UserRole
    mfa_required: bool = True
    mfa_setup_required: bool = False
    mfa_token: Optional[str] = None


class FaceVerificationRequest(BaseModel):
    temp_token: str
    image: str = Field(..., description="Base64 encoded JPEG image or data URL from live webcam")
    liveness_completed: Optional[bool] = True


class FaceVerificationResponse(BaseModel):
    verified: bool = True
    mfa_token: Optional[str] = None
    access_token: Optional[str] = None
    token_type: Optional[str] = "bearer"
    expires_in: Optional[int] = 3600
    user: Optional[CurrentUserResponse] = None
    mfa_required: bool = True
    mfa_setup_required: bool = False
    username: Optional[str] = None
    role: Optional[UserRole] = None


class FaceEnrollmentRequest(BaseModel):
    temp_token: str
    images: List[str] = Field(..., min_length=1, description="List of 1 to 5 base64 JPEG images from webcam")


class FaceEnrollmentResponse(BaseModel):
    enrolled: bool = True
    samples_processed: int
    message: str
    mfa_token: Optional[str] = None
    access_token: Optional[str] = None
    mfa_setup_required: bool = False
    username: Optional[str] = None
    user: Optional[CurrentUserResponse] = None


class MfaSetupResponse(BaseModel):
    secret: str
    qr_code_base64: str
    provisioning_uri: str
    username: str


class MfaEnableRequest(BaseModel):
    mfa_token: str
    secret: str
    code: str


class MfaVerifyRequest(BaseModel):
    mfa_token: str
    code: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: CurrentUserResponse
    face_token: Optional[str] = None
    face_verification_required: Optional[bool] = False
