from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.models.enums import UserRole
from app.schemas.zone import ZoneCreate, ZoneUpdate, ZoneResponse
from app.services.zone_service import ZoneService
from app.services.audit_service import AuditService
from app.api.deps import require_role

router = APIRouter()

# Role permissions
view_zones_role = require_role([UserRole.OPERATOR, UserRole.ANALYST, UserRole.ADMINISTRATOR])
manage_zones_role = require_role([UserRole.ADMINISTRATOR])


@router.get("/cameras/{camera_id}/zones", response_model=List[ZoneResponse])
def list_zones(
    camera_id: str,
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(view_zones_role)
):
    """
    List all polygon zones configured for a specific camera.
    """
    return ZoneService.list_zones(db, camera_id=camera_id, is_active=is_active)


@router.post("/cameras/{camera_id}/zones", response_model=ZoneResponse, status_code=status.HTTP_201_CREATED)
def create_zone(
    camera_id: str,
    zone_in: ZoneCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(manage_zones_role)
):
    """
    Configure a new restricted zone for a camera (Administrator only).
    """
    zone = ZoneService.create_zone(db, camera_id=camera_id, zone_in=zone_in)
    AuditService.log_action(
        db=db,
        user_id=current_user.id,
        action="ZONE_CREATED",
        resource_type="ZONE",
        resource_id=zone.id,
        metadata={"name": zone.name, "camera_id": camera_id}
    )
    return zone


@router.get("/zones/{zone_id}", response_model=ZoneResponse)
def get_zone(
    zone_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(view_zones_role)
):
    """
    Get detailed configuration of a zone by ID.
    """
    return ZoneService.get_zone(db, zone_id)


@router.patch("/zones/{zone_id}", response_model=ZoneResponse)
def update_zone(
    zone_id: str,
    zone_in: ZoneUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(manage_zones_role)
):
    """
    Update zone details (Administrator only).
    """
    zone = ZoneService.update_zone(db, zone_id, zone_in)
    AuditService.log_action(
        db=db,
        user_id=current_user.id,
        action="ZONE_UPDATED",
        resource_type="ZONE",
        resource_id=zone.id,
        metadata={"name": zone.name}
    )
    return zone


@router.delete("/zones/{zone_id}", response_model=ZoneResponse)
def delete_zone(
    zone_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(manage_zones_role)
):
    """
    Soft-delete a zone (marks as inactive to preserve historical records, Administrator only).
    """
    zone = ZoneService.delete_zone(db, zone_id)
    AuditService.log_action(
        db=db,
        user_id=current_user.id,
        action="ZONE_DEACTIVATED",
        resource_type="ZONE",
        resource_id=zone.id,
        metadata={"name": zone.name}
    )
    return zone
