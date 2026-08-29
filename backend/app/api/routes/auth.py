from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
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
    Returns temporary MFA challenge token requiring Step 2 verification.
    """
    return AuthService.authenticate_credentials(
        db=db,
        username_or_email=login_in.username_or_email,
        password=login_in.password,
    )


@router.get("/mfa/setup", response_model=MfaSetupResponse)
def get_mfa_setup(
    mfa_token: str = Query(..., description="Temporary MFA challenge token from Step 1"),
    db: Session = Depends(get_db),
):
    """
    Step 2 Setup: Generates TOTP secret, provisioning URI, and QR Code base64 image.
    """
    return AuthService.get_mfa_setup_payload(db=db, mfa_token=mfa_token)


@router.post("/mfa/enable", response_model=TokenResponse)
def enable_mfa(
    payload: MfaEnableRequest,
    db: Session = Depends(get_db),
):
    """
    Step 2 Activation: Verifies initial 6-digit TOTP code, activates MFA on account, and issues full session JWT.
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
    Step 2 Verification: Cryptographically verifies 6-digit TOTP code from Authenticator app and issues full session JWT.
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
    Retrieve profile and operational role details of the current authenticated operator.
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
