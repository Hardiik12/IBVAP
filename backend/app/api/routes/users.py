from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.models.enums import UserRole
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.services.user_service import UserService
from app.api.deps import require_role

router = APIRouter()

# Admin-only authorization dependency
admin_only = require_role([UserRole.ADMINISTRATOR])


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(admin_only)
):
    """
    Create a new system user (Administrator only).
    """
    return UserService.create_user(db, user_in=user_in, acting_admin_id=admin.id)


@router.get("", response_model=List[UserResponse])
def list_users(
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
    admin: User = Depends(admin_only)
):
    """
    List all system users with pagination (Administrator only).
    """
    return UserService.list_users(db, limit=limit, offset=offset)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(admin_only)
):
    """
    Retrieve user details by ID (Administrator only).
    """
    return UserService.get_user(db, user_id=user_id)


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: str,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(admin_only)
):
    """
    Update user attributes (Administrator only). Enforces protection against deactivating final active admin.
    """
    return UserService.update_user(db, user_id=user_id, user_in=user_in, acting_admin_id=admin.id)
