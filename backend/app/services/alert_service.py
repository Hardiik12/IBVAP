from datetime import datetime, timezone
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.alert import Alert
from app.models.event import Event
from app.models.enums import AlertStatus, EventSeverity
from app.schemas.alert import AlertUpdate


class AlertService:
    @staticmethod
    def create_alert_internal(db: Session, event: Event) -> Alert:
        """
        Internal service helper to automatically generate an active alert for an Event.
        Ensures 1:1 uniqueness mapping (prevents double alert generation).
        This does NOT commit immediately, allowing inclusion inside event transaction context.
        """
        existing = db.query(Alert).filter(Alert.event_id == event.id).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Alert already exists for this event"
            )

        alert = Alert(
            event_id=event.id,
            severity=event.severity,
            status=AlertStatus.ACTIVE,
            message="Intrusion detected in restricted zone."
        )
        db.add(alert)
        return alert

    @staticmethod
    def list_alerts(
        db: Session,
        status_filter: Optional[AlertStatus] = None,
        severity: Optional[EventSeverity] = None,
        camera_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Alert]:
        """
        List alerts sorted by created_at DESC with filtering and limit/offset pagination.
        Includes join on Event to support camera_id filtering.
        """
        # Sensible limits
        limit = min(max(1, limit), 100)
        offset = max(0, offset)

        query = db.query(Alert)

        if camera_id is not None:
            query = query.join(Event).filter(Event.camera_id == camera_id)
        if status_filter is not None:
            query = query.filter(Alert.status == status_filter)
        if severity is not None:
            query = query.filter(Alert.severity == severity)

        return query.order_by(Alert.created_at.desc()).offset(offset).limit(limit).all()

    @staticmethod
    def get_alert(db: Session, alert_id: str) -> Alert:
        """
        Get an alert by ID. Raises 404 if missing.
        """
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found"
            )
        return alert

    @staticmethod
    def update_alert(db: Session, alert_id: str, alert_in: AlertUpdate) -> Alert:
        """
        Update alert status and handle acknowledgment timestamping.
        """
        alert = AlertService.get_alert(db, alert_id)
        update_data = alert_in.model_dump(exclude_unset=True)

        if "status" in update_data:
            new_status = update_data["status"]
            if new_status == AlertStatus.ACKNOWLEDGED and alert.status != AlertStatus.ACKNOWLEDGED:
                alert.acknowledged_at = datetime.now(timezone.utc)
            alert.status = new_status

        if "acknowledged_by" in update_data:
            alert.acknowledged_by = update_data["acknowledged_by"]

        db.commit()
        db.refresh(alert)
        return alert
