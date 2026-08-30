from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    FaceVerificationRequest,
    FaceVerificationResponse,
    FaceEnrollmentRequest,
    FaceEnrollmentResponse,
    MfaSetupResponse,
    MfaEnableRequest,
    MfaVerifyRequest,
    TokenResponse,
    CurrentUserResponse,
)
from app.services.auth_service import AuthService
from app.services.audit_service import AuditService
from app.api.deps import get_current_user

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
def login(
    login_in: LoginRequest,
    db: Session = Depends(get_db),
):
    """
    Step 1: Authenticate operator credentials (Operator ID/Email + Password).
    Returns temporary challenge token (scope='password_verified') requiring Step 2 Face Verification.
    """
    return AuthService.authenticate_credentials(
        db=db,
        username_or_email=login_in.username_or_email,
        password=login_in.password,
    )


@router.post("/face/verify", response_model=FaceVerificationResponse)
def verify_face(
    payload: FaceVerificationRequest,
    db: Session = Depends(get_db),
):
    """
    Step 2: 1:1 Facial Biometric Verification.
    Verifies live webcam frame against the operator's enrolled facial reference profile.
    Upgrades challenge token to scope='face_verified' requiring Step 3 TOTP MFA.
    """
    return AuthService.verify_face_biometrics(
        db=db,
        temp_token=payload.temp_token,
        image_base64=payload.image,
    )


@router.post("/face/enroll", response_model=FaceEnrollmentResponse)
def enroll_face(
    payload: FaceEnrollmentRequest,
    db: Session = Depends(get_db),
):
    """
    Biometric Enrollment: Captures multiple facial samples to build and persist reference profile.
    """
    return AuthService.enroll_face_biometrics(
        db=db,
        temp_token=payload.temp_token,
        images=payload.images,
    )


@router.get("/mfa/setup", response_model=MfaSetupResponse)
def get_mfa_setup(
    mfa_token: str = Query(..., description="Temporary challenge token from Step 2"),
    db: Session = Depends(get_db),
):
    """
    Step 3 Setup: Generates TOTP secret, provisioning URI, and QR Code base64 image.
    """
    return AuthService.get_mfa_setup_payload(db=db, mfa_token=mfa_token)


@router.post("/mfa/enable", response_model=TokenResponse)
def enable_mfa(
    payload: MfaEnableRequest,
    db: Session = Depends(get_db),
):
    """
    Step 3 Activation: Verifies initial 6-digit TOTP code, activates MFA, and issues full session JWT.
    """
    return AuthService.enable_mfa_and_issue_session(
        db=db,
        mfa_token=payload.mfa_token,
        secret=payload.secret,
        code=payload.code,
    )


@router.post("/mfa/verify", response_model=TokenResponse)
def verify_mfa(
    payload: MfaVerifyRequest,
    db: Session = Depends(get_db),
):
    """
    Step 3 Verification: Cryptographically verifies rotating 6-digit TOTP code and issues full session JWT.
    """
    return AuthService.verify_mfa_and_issue_session(
        db=db,
        mfa_token=payload.mfa_token,
        code=payload.code,
    )


@router.get("/me", response_model=CurrentUserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve profile, biometric enrollment status, and operational role of authenticated operator.
    """
    return current_user


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Ends operator session and logs audit event.
    """
    AuditService.log_action(
        db=db,
        user_id=current_user.id,
        action="LOGOUT",
        resource_type="AUTH",
        resource_id=current_user.id,
        metadata={"username": current_user.username},
    )
    return {"message": "Session terminated successfully."}
