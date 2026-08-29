from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.models.enums import UserRole, EventType, EventSeverity, EventStatus
from app.schemas.event import EventCreate, EventUpdate, EventResponse
from app.services.event_service import EventService
from app.api.deps import require_role

router = APIRouter()

# Role permissions
view_events_role = require_role([UserRole.OPERATOR, UserRole.ANALYST, UserRole.ADMINISTRATOR, UserRole.AUDITOR])
manage_events_role = require_role([UserRole.OPERATOR, UserRole.ADMINISTRATOR])


def map_event_to_response(event) -> EventResponse:
    """Helper to inject computed alert_id into EventResponse."""
    return EventResponse(
        id=event.id,
        event_identifier=event.event_identifier,
        event_type=event.event_type,
        camera_id=event.camera_id,
        zone_id=event.zone_id,
        track_id=event.track_id,
        timestamp=event.timestamp,
        severity=event.severity,
        status=event.status,
        bounding_box=event.bounding_box,
        position=event.position,
        metadata=event.event_metadata,
        created_at=event.created_at,
        alert_id=event.alert.id if event.alert else None
    )


@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    event_in: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(manage_events_role)
):
    """
    Ingest a new security event (e.g. INTRUSION) from AI pipeline.
    Atomically generates associated alert if event_type is INTRUSION.
    """
    event = EventService.create_event(db, event_in)
    return map_event_to_response(event)


@router.get("", response_model=List[EventResponse])
def list_events(
    camera_id: Optional[str] = Query(None, description="Filter by camera ID"),
    zone_id: Optional[str] = Query(None, description="Filter by zone ID"),
    event_type: Optional[EventType] = Query(None, description="Filter by event type"),
    severity: Optional[EventSeverity] = Query(None, description="Filter by severity"),
    status: Optional[EventStatus] = Query(None, description="Filter by status"),
    start_time: Optional[datetime] = Query(None, description="Filter by timestamp start (ISO UTC)"),
    end_time: Optional[datetime] = Query(None, description="Filter by timestamp end (ISO UTC)"),
    limit: int = Query(20, description="Pagination limit (max 100)"),
    offset: int = Query(0, description="Pagination offset"),
    db: Session = Depends(get_db),
    current_user: User = Depends(view_events_role)
):
    """
    List all security events sorted by newest first, with query filters and pagination.
    """
    events = EventService.list_events(
        db,
        camera_id=camera_id,
        zone_id=zone_id,
        event_type=event_type,
        severity=severity,
        status_filter=status,
        start_time=start_time,
        end_time=end_time,
        limit=limit,
        offset=offset
    )
    return [map_event_to_response(e) for e in events]


@router.get("/{event_id}", response_model=EventResponse)
def get_event(
    event_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(view_events_role)
):
    """
    Retrieve details of a specific security event.
    """
    event = EventService.get_event(db, event_id)
    return map_event_to_response(event)


@router.patch("/{event_id}", response_model=EventResponse)
def update_event(
    event_id: str,
    event_in: EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(manage_events_role)
):
    """
    Update logically mutable fields of an event (status, severity, metadata).
    """
    event = EventService.update_event(db, event_id, event_in)
    return map_event_to_response(event)
