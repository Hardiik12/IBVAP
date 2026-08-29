from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import jwt

from app.models.user import User
from app.schemas.auth import (
    LoginResponse,
    MfaSetupResponse,
    TokenResponse,
    CurrentUserResponse,
)
from app.core import security
from app.core.config import settings
from app.services.audit_service import AuditService
from app.services.mfa_service import MfaService


class AuthService:
    @staticmethod
    def decode_mfa_token(mfa_token: str) -> Dict[str, Any]:
        """
        Validates temporary short-lived MFA challenge token.
        """
        payload = security.decode_access_token(mfa_token)
        if not payload or payload.get("scope") != "mfa_pending" or "sub" not in payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="MFA session expired or invalid. Please log in again.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload

    @staticmethod
    def authenticate_credentials(db: Session, username_or_email: str, password: str) -> LoginResponse:
        """
        Step 1: Authenticates operator ID/email + password.
        Enforces account lockout after consecutive failed attempts.
        Returns a short-lived MFA challenge token (scope: 'mfa_pending').
        """
        now = datetime.now(timezone.utc)
        user = db.query(User).filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()

        # Check account lockout
        if user and user.locked_until:
            locked_until_utc = user.locked_until
            if locked_until_utc.tzinfo is None:
                locked_until_utc = locked_until_utc.replace(tzinfo=timezone.utc)
            
            if locked_until_utc > now:
                remaining_min = int((locked_until_utc - now).total_seconds() / 60) + 1
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Security lockout active due to repeated failures. Try again in {remaining_min} minutes.",
                )
            else:
                # Lockout expired
                user.locked_until = None
                user.failed_login_attempts = 0
                db.commit()

        # Verify password
        if not user or not user.is_active or not security.verify_password(password, user.password_hash):
            if user:
                user.failed_login_attempts += 1
                if user.failed_login_attempts >= 5:
                    user.locked_until = now + timedelta(minutes=15)
                    AuditService.log_action(
                        db=db,
                        user_id=user.id,
                        action="ACCOUNT_LOCKED",
                        resource_type="AUTH",
                        metadata={"attempts": user.failed_login_attempts, "lockout_minutes": 15},
                    )
                db.commit()

            AuditService.log_action(
                db=db,
                user_id=user.id if user else None,
                action="LOGIN_FAILURE",
                resource_type="AUTH",
                metadata={"identifier": username_or_email},
            )

            # Generic error message — prevents user enumeration
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="ACCESS DENIED: Invalid operator credentials.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Credentials verified — issue temporary MFA challenge token (5 min expiry)
        temp_token_data = {
            "sub": user.id,
            "username": user.username,
            "role": user.role.value,
            "scope": "mfa_pending",
        }
        mfa_token = security.create_access_token(
            data=temp_token_data,
            expires_delta=timedelta(minutes=5),
        )

        AuditService.log_action(
            db=db,
            user_id=user.id,
            action="LOGIN_SUCCESS",
            resource_type="AUTH",
            resource_id=user.id,
            metadata={"username": user.username, "mfa_enabled": user.mfa_enabled},
        )

        return LoginResponse(
            mfa_required=True,
            mfa_setup_required=not user.mfa_enabled,
            mfa_token=mfa_token,
            temp_token_expires_in=300,
            username=user.username,
            role=user.role,
        )

    @staticmethod
    def get_mfa_setup_payload(db: Session, mfa_token: str) -> MfaSetupResponse:
        """
        Generates fresh TOTP secret, provisioning URI, and QR Code PNG for unconfigured operator.
        """
        payload = AuthService.decode_mfa_token(mfa_token)
        user_id = payload["sub"]
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive.")

        secret = MfaService.generate_totp_secret()
        uri = MfaService.generate_provisioning_uri(username=user.username, secret=secret)
        qr_code = MfaService.generate_qr_code_base64(uri)

        return MfaSetupResponse(
            secret=secret,
            qr_code_base64=qr_code,
            provisioning_uri=uri,
            username=user.username,
        )

    @staticmethod
    def enable_mfa_and_issue_session(db: Session, mfa_token: str, secret: str, code: str) -> TokenResponse:
        """
        Verifies initial 6-digit TOTP code, activates MFA for the account, and issues full session JWT.
        """
        payload = AuthService.decode_mfa_token(mfa_token)
        user_id = payload["sub"]
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive.")

        # Cryptographically verify the initial TOTP code against the provided secret
        if not MfaService.verify_totp_code(secret=secret, code=code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MFA SETUP FAILED: Invalid verification code. Ensure your device clock is accurate and try again.",
            )

        # Activate MFA on user record
        user.mfa_secret = secret
        user.mfa_enabled = True
        user.failed_login_attempts = 0
        user.locked_until = None
        db.commit()
        db.refresh(user)

        AuditService.log_action(
            db=db,
            user_id=user.id,
            action="MFA_ENABLED",
            resource_type="AUTH",
            resource_id=user.id,
            metadata={"username": user.username},
        )

        return AuthService.create_full_session_token(db=db, user=user)

    @staticmethod
    def verify_mfa_and_issue_session(db: Session, mfa_token: str, code: str) -> TokenResponse:
        """
        Step 2: Verifies 6-digit TOTP code for MFA-enabled operator, issuing full session JWT.
        """
        payload = AuthService.decode_mfa_token(mfa_token)
        user_id = payload["sub"]
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive.")

        if not user.mfa_enabled or not user.mfa_secret:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MFA is not configured for this account. Please complete setup first.",
            )

        # Verify rotating 6-digit TOTP
        if not MfaService.verify_totp_code(secret=user.mfa_secret, code=code):
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= 5:
                user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=15)
            db.commit()

            AuditService.log_action(
                db=db,
                user_id=user.id,
                action="MFA_FAILURE",
                resource_type="AUTH",
                resource_id=user.id,
                metadata={"username": user.username, "attempts": user.failed_login_attempts},
            )

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="MFA VERIFICATION FAILED: The security code is invalid or expired.",
            )

        # Successful MFA verification
        user.failed_login_attempts = 0
        user.locked_until = None
        db.commit()

        AuditService.log_action(
            db=db,
            user_id=user.id,
            action="LOGIN_SUCCESS",
            resource_type="AUTH",
            resource_id=user.id,
            metadata={"username": user.username, "role": user.role.value, "mfa_verified": True},
        )

        return AuthService.create_full_session_token(db=db, user=user)

    @staticmethod
    def create_full_session_token(db: Session, user: User) -> TokenResponse:
        """
        Generates signed authoritative JWT access token with scope='fully_authenticated'.
        """
        expires_minutes = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        payload = {
            "sub": user.id,
            "username": user.username,
            "role": user.role.value,
            "scope": "fully_authenticated",
            "mfa_verified": True,
        }
        access_token = security.create_access_token(data=payload)

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=expires_minutes * 60,
            user=CurrentUserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                role=user.role,
                mfa_enabled=user.mfa_enabled,
                is_active=user.is_active,
                created_at=user.created_at,
                updated_at=user.updated_at,
            ),
        )
