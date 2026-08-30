from datetime import datetime, timezone
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.event import Event
from app.models.camera import Camera
from app.models.zone import Zone
from app.models.enums import EventType, EventSeverity, EventStatus
from app.schemas.event import EventCreate, EventUpdate
from app.services.camera_service import CameraService
from app.services.zone_service import ZoneService
from app.services.alert_service import AlertService


class EventService:
    @staticmethod
    def create_event(db: Session, event_in: EventCreate) -> Event:
        """
        Create a new event within an atomic transaction.
        Enforces camera existence, zone camera matching, and event_identifier uniqueness.
        Generates associated Alert automatically on INTRUSION.
        """
        # 1. Verify camera exists
        CameraService.get_camera(db, event_in.camera_id)

        # 2. Verify zone exists if supplied, and ensure it belongs to the camera
        if event_in.zone_id is not None:
            zone = ZoneService.get_zone(db, event_in.zone_id)
            if zone.camera_id != event_in.camera_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Zone does not belong to camera"
                )

        # 3. Verify event_identifier uniqueness
        existing = db.query(Event).filter(Event.event_identifier == event_in.event_identifier).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Event identifier already exists"
            )

        try:
            # Construct Event object mapping aliased event_metadata
            event = Event(
                event_identifier=event_in.event_identifier,
                event_type=event_in.event_type,
                camera_id=event_in.camera_id,
                zone_id=event_in.zone_id,
                track_id=event_in.track_id,
                timestamp=event_in.timestamp,
                severity=event_in.severity,
                status=event_in.status,
                bounding_box=event_in.bounding_box,
                position=event_in.position,
                event_metadata=event_in.event_metadata
            )
            db.add(event)
            db.flush()  # Populates event.id for Alert relationship

            # 4. Create Alert if event_type is INTRUSION
            if event.event_type == EventType.INTRUSION:
                AlertService.create_alert_internal(db, event)

            db.commit()
            db.refresh(event)

            # Broadcast WebSocket notification strictly after successful database commit
            try:
                from app.services.notification_service import NotificationService
                NotificationService.notify_event_created(event)
            except Exception as notify_err:
                # Log broadcast error without failing the already committed DB transaction
                import logging
                logging.getLogger(__name__).warning(f"Failed to trigger event broadcast: {notify_err}")

            return event
        except Exception as e:
            db.rollback()
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database write failed: {str(e)}"
            )

    @staticmethod
    def list_events(
        db: Session,
        camera_id: Optional[str] = None,
        zone_id: Optional[str] = None,
        event_type: Optional[EventType] = None,
        severity: Optional[EventSeverity] = None,
        status_filter: Optional[EventStatus] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Event]:
        """
        List events sorted by timestamp DESC with filtering and pagination.
        Max limit defaulted to 100.
        """
        limit = min(max(1, limit), 100)
        offset = max(0, offset)

        query = db.query(Event)

        if camera_id is not None:
            query = query.filter(Event.camera_id == camera_id)
        if zone_id is not None:
            query = query.filter(Event.zone_id == zone_id)
        if event_type is not None:
            query = query.filter(Event.event_type == event_type)
        if severity is not None:
            query = query.filter(Event.severity == severity)
        if status_filter is not None:
            query = query.filter(Event.status == status_filter)
        if start_time is not None:
            query = query.filter(Event.timestamp >= start_time)
        if end_time is not None:
            query = query.filter(Event.timestamp <= end_time)

        return query.order_by(Event.timestamp.desc()).offset(offset).limit(limit).all()

    @staticmethod
    def get_event(db: Session, event_id: str) -> Event:
        """
        Fetch an event by ID. Raises 404 if missing.
        """
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
        return event

    @staticmethod
    def update_event(db: Session, event_id: str, event_in: EventUpdate) -> Event:
        """
        Update logically mutable event fields (status, severity, metadata).
        """
        event = EventService.get_event(db, event_id)
        update_data = event_in.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(event, key, value)

        db.commit()
        db.refresh(event)
        return event

    @staticmethod
    def clear_events(db: Session, user_id: Optional[str] = None) -> int:
        """
        Permanently clear all forensic events from the database (Administrator only).
        """
        count = db.query(Event).delete(synchronize_session=False)
        db.commit()
        if user_id:
            from app.services.audit_service import AuditService
            AuditService.log_action(
                db=db,
                user_id=user_id,
                action="EVENTS_CLEARED",
                resource_type="EVENT",
                metadata={"cleared_count": count},
            )
        return count
