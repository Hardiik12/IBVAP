from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.auth import TokenResponse
from app.core import security
from app.core.config import settings
from app.services.audit_service import AuditService


class AuthService:
    @staticmethod
    def authenticate_user(db: Session, username_or_email: str, password: str) -> User:
        """
        Verifies credentials against username or email identifiers.
        Enforces active check and generic failure messages to avoid user enumeration.
        """
        # Look up user by username OR email
        user = db.query(User).filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()

        if not user or not user.is_active or not security.verify_password(password, user.password_hash):
            # Log failed login attempt
            AuditService.log_action(
                db=db,
                user_id=user.id if user else None,
                action="LOGIN_FAILURE",
                resource_type="AUTH",
                metadata={"identifier": username_or_email}
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )

        # Log successful login
        AuditService.log_action(
            db=db,
            user_id=user.id,
            action="LOGIN_SUCCESS",
            resource_type="AUTH",
            resource_id=user.id,
            metadata={"username": user.username, "role": user.role.value}
        )

        return user

    @staticmethod
    def create_token_for_user(user: User) -> TokenResponse:
        """
        Generates JWT access token for authenticated user.
        """
        expires_minutes = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        payload = {
            "sub": user.id,
            "username": user.username,
            "role": user.role.value
        }
        access_token = security.create_access_token(data=payload)
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=expires_minutes * 60
        )
