from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.models.enums import UserRole, EventSeverity, AlertStatus
from app.schemas.alert import AlertUpdate, AlertResponse
from app.services.alert_service import AlertService
from app.services.audit_service import AuditService
from app.api.deps import require_role

router = APIRouter()

# Role permissions
view_alerts_role = require_role([UserRole.OPERATOR, UserRole.ANALYST, UserRole.ADMINISTRATOR, UserRole.AUDITOR])
manage_alerts_role = require_role([UserRole.OPERATOR, UserRole.ADMINISTRATOR])


@router.get("", response_model=List[AlertResponse])
def list_alerts(
    status: Optional[AlertStatus] = Query(None, description="Filter by alert status"),
    severity: Optional[EventSeverity] = Query(None, description="Filter by severity"),
    camera_id: Optional[str] = Query(None, description="Filter by source camera ID"),
    limit: int = Query(20, description="Pagination limit (max 100)"),
    offset: int = Query(0, description="Pagination offset"),
    db: Session = Depends(get_db),
    current_user: User = Depends(view_alerts_role)
):
    """
    List all generated alarms/alerts sorted by newest first, with query filters and pagination.
    """
    return AlertService.list_alerts(
        db,
        status_filter=status,
        severity=severity,
        camera_id=camera_id,
        limit=limit,
        offset=offset
    )


@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert(
    alert_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(view_alerts_role)
):
    """
    Retrieve details of a specific security alert.
    """
    return AlertService.get_alert(db, alert_id)


@router.patch("/{alert_id}", response_model=AlertResponse)
def update_alert(
    alert_id: str,
    alert_in: AlertUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(manage_alerts_role)
):
    """
    Update alert status (e.g. ACKNOWLEDGED, RESOLVED) and record acknowledgement timestamps.
    """
    if alert_in.status == AlertStatus.ACKNOWLEDGED and not alert_in.acknowledged_by:
        alert_in.acknowledged_by = current_user.id

    alert = AlertService.update_alert(db, alert_id, alert_in)

    if alert_in.status == AlertStatus.ACKNOWLEDGED:
        AuditService.log_action(
            db=db,
            user_id=current_user.id,
            action="ALERT_ACKNOWLEDGED",
            resource_type="ALERT",
            resource_id=alert.id,
            metadata={"acknowledged_by": current_user.username}
        )

    return alert
