from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.models.enums import UserRole
from app.schemas.audit_log import AuditLogResponse
from app.services.audit_service import AuditService
from app.api.deps import require_role

router = APIRouter()

# Read-only audit access dependency for Administrator and Auditor roles
auditor_or_admin = require_role([UserRole.ADMINISTRATOR, UserRole.AUDITOR])


def map_audit_log_to_response(log) -> AuditLogResponse:
    """Helper to cleanly serialize audit log entries."""
    return AuditLogResponse(
        id=log.id,
        user_id=log.user_id,
        action=log.action,
        resource_type=log.resource_type,
        resource_id=log.resource_id,
        timestamp=log.timestamp,
        metadata=log.log_metadata
    )


@router.get("", response_model=List[AuditLogResponse])
def list_audit_logs(
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(auditor_or_admin)
):
    """
    List audit logs with filtering and pagination (Administrator and Auditor only).
    """
    logs = AuditService.list_audit_logs(
        db=db,
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        start_time=start_time,
        end_time=end_time,
        limit=limit,
        offset=offset
    )
    return [map_audit_log_to_response(l) for l in logs]


@router.delete("", status_code=200)
def clear_audit_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMINISTRATOR]))
):
    """
    Permanently clear all audit log entries (Administrator only).
    """
    cleared_count = AuditService.clear_audit_logs(db=db, user_id=current_user.id)
    return {"message": "Audit logs cleared successfully", "cleared_count": cleared_count}

