from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse, CurrentUserResponse
from app.services.auth_service import AuthService
from app.api.deps import get_current_user

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login(
    login_in: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user with username/email and password, returning JWT access token.
    """
    user = AuthService.authenticate_user(
        db=db,
        username_or_email=login_in.username_or_email,
        password=login_in.password
    )
    return AuthService.create_token_for_user(user)


@router.get("/me", response_model=CurrentUserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve profile details of the current authenticated user.
    """
    return current_user
