from typing import List, Callable, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core import security
from app.models.user import User
from app.models.enums import UserRole

# OAuth2 scheme extracting Bearer token from HTTP Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def get_current_user(
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme),
) -> User:
    """
    Decodes Bearer JWT access token and retrieves active authenticated user.
    Strictly verifies that the full authentication pipeline has been completed (scope == 'fully_authenticated').
    """
    if token:
        payload = security.decode_access_token(token)
        if payload and "sub" in payload:
            # Check scope — reject any partial stage tokens (password_verified, face_verified, mfa_pending)
            if payload.get("scope") != "fully_authenticated":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Full biometric and MFA authentication required before accessing this resource.",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            user_id = payload["sub"]
            user = db.query(User).filter(User.id == user_id).first()
            if user and user.is_active:
                return user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication credentials were not provided or have expired.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def require_role(allowed_roles: List[UserRole]) -> Callable:
    """
    Returns a dependency enforcing Role-Based Access Control (RBAC).
    Raises 403 Forbidden if user's role is not within allowed_roles.
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to perform this action",
            )
        return current_user

    return role_checker
