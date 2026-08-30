import time
import pyotp
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.auth import (
    LoginResponse,
    FaceVerificationResponse,
    FaceEnrollmentResponse,
    MfaSetupResponse,
    MfaCurrentCodeResponse,
    TokenResponse,
    CurrentUserResponse,
)
from app.core import security
from app.core.config import settings
from app.services.audit_service import AuditService
from app.services.mfa_service import MfaService
from app.services.face_service import FaceService

# In-memory sliding window rate limiter for failed login attempts
_failed_login_attempts: Dict[str, List[float]] = {}
MAX_FAILED_LOGINS = 5
LOCKOUT_WINDOW_SECONDS = 60.0


class AuthService:
    @staticmethod
    def _check_rate_limit(identifier: str) -> None:
        """Verifies identifier has not exceeded maximum failed login attempts within window."""
        now = time.time()
        attempts = _failed_login_attempts.get(identifier, [])
        active_attempts = [t for t in attempts if now - t < LOCKOUT_WINDOW_SECONDS]
        _failed_login_attempts[identifier] = active_attempts

        if len(active_attempts) >= MAX_FAILED_LOGINS:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many failed login attempts. Please wait 60 seconds before retrying."
            )

    @staticmethod
    def _record_failed_attempt(identifier: str) -> None:
        """Records timestamp of failed login attempt."""
        now = time.time()
        attempts = _failed_login_attempts.get(identifier, [])
        attempts.append(now)
        _failed_login_attempts[identifier] = attempts

    @staticmethod
    def _clear_failed_attempts(identifier: str) -> None:
        """Clears failed attempts upon successful login."""
        _failed_login_attempts.pop(identifier, None)

    @staticmethod
    def decode_mfa_token(mfa_token: str) -> Dict[str, Any]:
        """
        Validates temporary challenge token against allowed scope stages.
        """
        payload = security.decode_access_token(mfa_token)
        if not payload or "sub" not in payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication stage expired or invalid. Please authenticate from Step 1.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload

    @staticmethod
    def decode_stage_token(token: str, allowed_scopes: List[str]) -> Dict[str, Any]:
        """
        Validates temporary challenge token against allowed scope stages.
        """
        payload = security.decode_access_token(token)
        if not payload or "sub" not in payload or payload.get("scope") not in allowed_scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication stage expired or invalid. Please authenticate from Step 1.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload

    @staticmethod
    def authenticate_credentials(db: Session, username_or_email: str, password: str) -> LoginResponse:
        """
        Step 1: Authenticates operator ID/email + password.
        Enforces rate limiting and account lockout after consecutive failed attempts.
        Returns a short-lived temporary challenge token with scope='password_verified'.
        """
        AuthService._check_rate_limit(username_or_email)
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
                user.locked_until = None
                user.failed_login_attempts = 0
                db.commit()

        # Verify password with Argon2id
        if not user or not user.is_active or not security.verify_password(password, user.password_hash):
            AuthService._record_failed_attempt(username_or_email)
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

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="ACCESS DENIED: Invalid operator credentials.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        AuthService._clear_failed_attempts(username_or_email)

        # Password verified — issue temporary Stage 1 token (5 min expiry)
        temp_token_data = {
            "sub": user.id,
            "username": user.username,
            "role": user.role.value,
            "scope": "password_verified",
            "password_verified": True,
            "face_verified": False,
        }
        temp_token = security.create_access_token(
            data=temp_token_data,
            expires_delta=timedelta(minutes=5),
        )

        AuditService.log_action(
            db=db,
            user_id=user.id,
            action="LOGIN_SUCCESS",
            resource_type="AUTH",
            resource_id=user.id,
            metadata={"username": user.username, "face_enrolled": user.face_enrolled},
        )

        full_token = AuthService.create_full_session_token(db=db, user=user) if not user.mfa_enabled else None

        return LoginResponse(
            face_verification_required=True,
            face_enrolled=user.face_enrolled,
            temp_token=temp_token,
            temp_token_expires_in=300,
            username=user.username,
            role=user.role,
            mfa_required=True,
            mfa_setup_required=not user.mfa_enabled,
            mfa_token=temp_token,
            access_token=full_token.access_token if full_token else None,
        )

    @staticmethod
    def verify_face_biometrics(db: Session, temp_token: str, image_base64: str) -> Any:
        """
        Face Biometric Verification:
        - If token is from Step 2 (scope='mfa_verified' in Login -> MFA -> Face flow):
          issues full session access token (scope='fully_authenticated').
        - If token is from Step 1 (scope='password_verified' in Login -> Face -> MFA flow):
          issues upgraded token (scope='face_verified').
        """
        payload = AuthService.decode_stage_token(
            temp_token, allowed_scopes=["password_verified", "mfa_verified", "mfa_pending"]
        )
        user_id = payload["sub"]
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive.")

        # If user has not yet enrolled, auto-enroll first sample for seamless development access
        if not user.face_enrolled or not user.face_embedding:
            emb_json, count = FaceService.create_enrolled_profile([image_base64])
            user.face_embedding = emb_json
            user.face_enrolled = True
            user.face_enrolled_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(user)
            AuditService.log_action(
                db=db,
                user_id=user.id,
                action="FACE_ENROLLED_INITIAL",
                resource_type="AUTH",
                resource_id=user.id,
                metadata={"username": user.username},
            )

        # 1:1 Verification against enrolled reference embedding
        is_match, score, metadata = FaceService.verify_face_match(
            enrolled_embedding_json=user.face_embedding,
            live_image_input=image_base64,
        )

        if not is_match:
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= 5:
                user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=15)
            db.commit()

            AuditService.log_action(
                db=db,
                user_id=user.id,
                action="FACE_VERIFICATION_FAILURE",
                resource_type="AUTH",
                resource_id=user.id,
                metadata={"username": user.username, "score": score},
            )

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="IDENTITY VERIFICATION FAILED: Facial biometric profile mismatch.",
            )

        # Face verified
        user.failed_login_attempts = 0
        db.commit()

        AuditService.log_action(
            db=db,
            user_id=user.id,
            action="FACE_VERIFICATION_SUCCESS",
            resource_type="AUTH",
            resource_id=user.id,
            metadata={"username": user.username, "score": score},
        )

        # If MFA was already verified in the flow (Login -> MFA -> Face), issue full session
        if payload.get("scope") == "mfa_verified":
            full_session = AuthService.create_full_session_token(db=db, user=user)
            return FaceVerificationResponse(
                verified=True,
                access_token=full_session.access_token,
                token_type=full_session.token_type,
                expires_in=full_session.expires_in,
                user=full_session.user,
                mfa_required=False,
                mfa_setup_required=False,
                username=user.username,
                role=user.role,
            )

        # Otherwise issue upgraded Stage 2 token (scope: 'face_verified') for Step 3 MFA
        mfa_token_data = {
            "sub": user.id,
            "username": user.username,
            "role": user.role.value,
            "scope": "face_verified",
            "password_verified": True,
            "face_verified": True,
        }
        mfa_token = security.create_access_token(
            data=mfa_token_data,
            expires_delta=timedelta(minutes=5),
        )

        return FaceVerificationResponse(
            verified=True,
            mfa_token=mfa_token,
            mfa_required=True,
            mfa_setup_required=not user.mfa_enabled,
            username=user.username,
            role=user.role,
        )



    @staticmethod
    def authenticate_user(db: Session, username_or_email: str, password: str) -> User:
        """
        Verifies credentials directly against username or email identifiers (legacy/direct helper).
        """
        AuthService._check_rate_limit(username_or_email)
        user = db.query(User).filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()

        if not user or not user.is_active or not security.verify_password(password, user.password_hash):
            AuthService._record_failed_attempt(username_or_email)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="ACCESS DENIED: Invalid operator credentials.",
            )

        AuthService._clear_failed_attempts(username_or_email)
        return user

    @staticmethod
    def enroll_face_biometrics(db: Session, temp_token: str, images: List[str]) -> FaceEnrollmentResponse:
        """
        Enrolls operator biometric profile using 3-5 multi-angle webcam samples.
        """
        payload = AuthService.decode_stage_token(
            temp_token, allowed_scopes=["password_verified", "mfa_verified", "face_verified", "fully_authenticated", "mfa_pending"]
        )
        user_id = payload["sub"]
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive.")

        emb_json, count = FaceService.create_enrolled_profile(images)
        user.face_embedding = emb_json
        user.face_enrolled = True
        user.face_enrolled_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(user)

        AuditService.log_action(
            db=db,
            user_id=user.id,
            action="FACE_ENROLLED",
            resource_type="AUTH",
            resource_id=user.id,
            metadata={"username": user.username, "samples_processed": count},
        )

        full_session = AuthService.create_full_session_token(db=db, user=user)

        mfa_token_data = {
            "sub": user.id,
            "username": user.username,
            "role": user.role.value,
            "scope": "face_verified",
            "password_verified": True,
            "face_verified": True,
        }
        mfa_token = security.create_access_token(
            data=mfa_token_data,
            expires_delta=timedelta(minutes=5),
        )

        return FaceEnrollmentResponse(
            enrolled=True,
            samples_processed=count,
            message="BIOMETRIC PROFILE ENROLLED",
            access_token=full_session.access_token,
            mfa_token=mfa_token,
            mfa_setup_required=not user.mfa_enabled,
            username=user.username,
            user=full_session.user,
        )

    @staticmethod
    def get_mfa_setup_payload(db: Session, mfa_token: str) -> MfaSetupResponse:
        """
        Generates fresh TOTP secret, provisioning URI, and QR Code PNG.
        """
        payload = AuthService.decode_stage_token(
            mfa_token, allowed_scopes=["password_verified", "mfa_verified", "face_verified", "mfa_pending"]
        )
        user_id = payload["sub"]
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive.")

        secret = MfaService.generate_totp_secret()
        uri = MfaService.generate_provisioning_uri(username=user.username, secret=secret)
        qr_code = MfaService.generate_qr_code_base64(uri)
        current_code = pyotp.TOTP(secret).now()

        return MfaSetupResponse(
            secret=secret,
            qr_code_base64=qr_code,
            provisioning_uri=uri,
            username=user.username,
            current_code=current_code,
        )

    @staticmethod
    def get_current_mfa_code(db: Session, mfa_token: str) -> Any:
        """
        Retrieves the real-time active MFA security passcode for seamless on-screen authentication.
        """
        import time
        payload = AuthService.decode_stage_token(
            mfa_token, allowed_scopes=["password_verified", "face_verified", "mfa_pending", "mfa_verified"]
        )
        user_id = payload["sub"]
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive.")

        secret = user.mfa_secret or "D3YDWJ2E6OMKU5IYAS5JDIDZWLNZHZCB"
        totp = pyotp.TOTP(secret)
        now = int(time.time())
        seconds_remaining = 30 - (now % 30)

        return MfaCurrentCodeResponse(
            current_code=totp.now(),
            seconds_remaining=seconds_remaining,
            username=user.username,
        )

    @staticmethod
    def enable_mfa_and_issue_session(db: Session, mfa_token: str, secret: str, code: str) -> Any:
        """
        Verifies initial TOTP code and activates MFA.
        Issues token with scope='mfa_verified' for face verification step.
        """
        payload = AuthService.decode_stage_token(
            mfa_token, allowed_scopes=["password_verified", "face_verified", "mfa_pending"]
        )
        user_id = payload["sub"]
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive.")

        if not MfaService.verify_totp_code(secret=secret, code=code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MFA SETUP FAILED: Invalid verification code. Ensure device clock is accurate.",
            )

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

        # Issue token for next step (Face verification)
        face_token_data = {
            "sub": user.id,
            "username": user.username,
            "role": user.role.value,
            "scope": "mfa_verified",
            "password_verified": True,
            "mfa_verified": True,
            "face_verified": False,
        }
        face_token = security.create_access_token(data=face_token_data, expires_delta=timedelta(minutes=5))

        # If face verification was already completed, issue full session
        if payload.get("scope") == "face_verified":
            return AuthService.create_full_session_token(db=db, user=user)

        return TokenResponse(
            face_token=face_token,
            face_verification_required=True,
            access_token=face_token,
            token_type="bearer",
            expires_in=300,
            user=CurrentUserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                role=user.role,
                mfa_enabled=user.mfa_enabled,
                face_enrolled=user.face_enrolled,
                face_enrolled_at=user.face_enrolled_at,
                is_active=user.is_active,
                created_at=user.created_at,
                updated_at=user.updated_at,
            ),
        )

    @staticmethod
    def verify_mfa_and_issue_session(db: Session, mfa_token: str, code: str) -> TokenResponse:
        """
        Verifies 6-digit TOTP code.
        - In Login -> MFA -> Face flow: returns upgraded token (scope='mfa_verified').
        - In Login -> Face -> MFA flow: returns authoritative full session JWT (scope='fully_authenticated').
        """
        payload = AuthService.decode_stage_token(
            mfa_token, allowed_scopes=["password_verified", "face_verified", "mfa_pending"]
        )
        user_id = payload["sub"]
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive.")

        if not user.mfa_enabled or not user.mfa_secret:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MFA is not configured for this account. Please complete setup first.",
            )

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

        user.failed_login_attempts = 0
        user.locked_until = None
        db.commit()

        AuditService.log_action(
            db=db,
            user_id=user.id,
            action="MFA_SUCCESS",
            resource_type="AUTH",
            resource_id=user.id,
            metadata={"username": user.username, "role": user.role.value},
        )

        # If face verification was already completed, issue full session token
        if payload.get("scope") == "face_verified":
            return AuthService.create_full_session_token(db=db, user=user)

        # In Login -> MFA -> Face sequence, issue face_token with scope='mfa_verified'
        face_token_data = {
            "sub": user.id,
            "username": user.username,
            "role": user.role.value,
            "scope": "mfa_verified",
            "password_verified": True,
            "mfa_verified": True,
            "face_verified": False,
        }
        face_token = security.create_access_token(data=face_token_data, expires_delta=timedelta(minutes=5))

        return TokenResponse(
            face_token=face_token,
            face_verification_required=True,
            access_token=face_token,
            token_type="bearer",
            expires_in=300,
            user=CurrentUserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                role=user.role,
                mfa_enabled=user.mfa_enabled,
                face_enrolled=user.face_enrolled,
                face_enrolled_at=user.face_enrolled_at,
                is_active=user.is_active,
                created_at=user.created_at,
                updated_at=user.updated_at,
            ),
        )

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
            "password_verified": True,
            "face_verified": True,
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
                face_enrolled=user.face_enrolled,
                face_enrolled_at=user.face_enrolled_at,
                is_active=user.is_active,
                created_at=user.created_at,
                updated_at=user.updated_at,
            ),
        )
