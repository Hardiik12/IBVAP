from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.enums import UserRole
from app.schemas.user import UserCreate, UserUpdate
from app.core import security
from app.services.audit_service import AuditService


class UserService:
    @staticmethod
    def create_user(db: Session, user_in: UserCreate, acting_admin_id: Optional[str] = None) -> User:
        """
        Create a new system user with Argon2id hashed password.
        Enforces uniqueness checks on username and email.
        """
        # Check username uniqueness
        if db.query(User).filter(User.username == user_in.username).first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already exists"
            )

        # Check email uniqueness
        if db.query(User).filter(User.email == user_in.email).first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists"
            )

        hashed_pwd = security.hash_password(user_in.password)

        user = User(
            username=user_in.username,
            email=user_in.email,
            password_hash=hashed_pwd,
            role=user_in.role,
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # Audit log user creation
        AuditService.log_action(
            db=db,
            user_id=acting_admin_id,
            action="USER_CREATED",
            resource_type="USER",
            resource_id=user.id,
            metadata={"created_username": user.username, "role": user.role.value}
        )

        return user

    @staticmethod
    def get_user(db: Session, user_id: str) -> User:
        """
        Fetch a user by ID. Raises 404 if missing.
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user

    @staticmethod
    def list_users(db: Session, limit: int = 20, offset: int = 0) -> List[User]:
        """
        List all system users with pagination.
        """
        return db.query(User).order_by(User.created_at.desc()).offset(offset).limit(limit).all()

    @staticmethod
    def update_user(db: Session, user_id: str, user_in: UserUpdate, acting_admin_id: Optional[str] = None) -> User:
        """
        Update user attributes. Enforces protection preventing deactivating or demoting the final active administrator.
        """
        user = UserService.get_user(db, user_id)

        # Check if this change would deactivate or demote an administrator
        would_deactivate = user_in.is_active is False and user.is_active
        would_demote = user_in.role is not None and user_in.role != UserRole.ADMINISTRATOR and user.role == UserRole.ADMINISTRATOR

        if user.role == UserRole.ADMINISTRATOR and (would_deactivate or would_demote):
            active_admin_count = db.query(User).filter(
                User.role == UserRole.ADMINISTRATOR,
                User.is_active.is_(True)
            ).count()

            if active_admin_count <= 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot deactivate or demote the last active administrator"
                )

        update_data = user_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(user, key, value)

        db.commit()
        db.refresh(user)

        # Audit log user update
        AuditService.log_action(
            db=db,
            user_id=acting_admin_id,
            action="USER_UPDATED",
            resource_type="USER",
            resource_id=user.id,
            metadata={"updated_fields": list(update_data.keys()), "target_username": user.username}
        )

        return user
