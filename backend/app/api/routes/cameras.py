from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.models.enums import UserRole
from app.schemas.camera import CameraCreate, CameraUpdate, CameraResponse
from app.services.camera_service import CameraService
from app.services.audit_service import AuditService
from app.api.deps import require_role

router = APIRouter()

# Role permissions
view_cameras_role = require_role([UserRole.OPERATOR, UserRole.ANALYST, UserRole.ADMINISTRATOR])
manage_cameras_role = require_role([UserRole.ADMINISTRATOR])


@router.get("", response_model=List[CameraResponse])
def list_cameras(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(view_cameras_role)
):
    """
    List all cameras, optionally filtered by active status.
    """
    return CameraService.list_cameras(db, is_active=is_active)


@router.post("", response_model=CameraResponse, status_code=status.HTTP_201_CREATED)
def create_camera(
    camera_in: CameraCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(manage_cameras_role)
):
    """
    Create a new camera feed configuration (Administrator only).
    """
    camera = CameraService.create_camera(db, camera_in)
    AuditService.log_action(
        db=db,
        user_id=current_user.id,
        action="CAMERA_CREATED",
        resource_type="CAMERA",
        resource_id=camera.id,
        metadata={"camera_identifier": camera.camera_identifier, "name": camera.name}
    )
    return camera


@router.get("/{camera_id}", response_model=CameraResponse)
def get_camera(
    camera_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(view_cameras_role)
):
    """
    Get details of a camera by ID.
    """
    return CameraService.get_camera(db, camera_id)


@router.patch("/{camera_id}", response_model=CameraResponse)
def update_camera(
    camera_id: str,
    camera_in: CameraUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(manage_cameras_role)
):
    """
    Update camera fields, maintaining identifier uniqueness (Administrator only).
    """
    camera = CameraService.update_camera(db, camera_id, camera_in)
    AuditService.log_action(
        db=db,
        user_id=current_user.id,
        action="CAMERA_UPDATED",
        resource_type="CAMERA",
        resource_id=camera.id,
        metadata={"camera_identifier": camera.camera_identifier}
    )
    return camera


@router.delete("/{camera_id}", response_model=CameraResponse)
def delete_camera(
    camera_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(manage_cameras_role)
):
    """
    Soft-delete a camera (marks as inactive to preserve historical records, Administrator only).
    """
    camera = CameraService.delete_camera(db, camera_id)
    AuditService.log_action(
        db=db,
        user_id=current_user.id,
        action="CAMERA_DEACTIVATED",
        resource_type="CAMERA",
        resource_id=camera.id,
        metadata={"camera_identifier": camera.camera_identifier}
    )
    return camera
