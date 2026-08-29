import logging
import asyncio
from typing import Optional
from app.models.event import Event
from app.models.enums import EventType
from app.schemas.event import EventResponse
from app.schemas.alert import AlertResponse
from app.services.websocket_manager import websocket_manager

logger = logging.getLogger(__name__)


class NotificationService:
    @staticmethod
    def map_event_to_response(event: Event) -> EventResponse:
        """Helper to convert Event ORM object to EventResponse schema."""
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

    @staticmethod
    def map_alert_to_response(alert) -> Optional[AlertResponse]:
        """Helper to convert Alert ORM object to AlertResponse schema."""
        if not alert:
            return None
        return AlertResponse(
            id=alert.id,
            event_id=alert.event_id,
            severity=alert.severity,
            status=alert.status,
            message=alert.message,
            created_at=alert.created_at,
            acknowledged_at=alert.acknowledged_at,
            acknowledged_by=alert.acknowledged_by
        )

    @classmethod
    async def broadcast_event_async(cls, event: Event) -> None:
        """
        Asynchronously constructs and broadcasts real-time event/alert JSON notification payload.
        """
        msg_type = "INTRUSION_ALERT" if event.event_type == EventType.INTRUSION else "EVENT_CREATED"

        event_resp = cls.map_event_to_response(event)
        alert_resp = cls.map_alert_to_response(event.alert)

        payload = {
            "type": msg_type,
            "timestamp": event.timestamp.isoformat(),
            "event": event_resp.model_dump(mode="json"),
            "alert": alert_resp.model_dump(mode="json") if alert_resp else None
        }

        await websocket_manager.broadcast(payload)

    @classmethod
    def notify_event_created(cls, event: Event) -> None:
        """
        Synchronous wrapper called after DB commit. Schedules async broadcast on running loop
        or executes cleanly if loop is running.
        """
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(cls.broadcast_event_async(event))
        except RuntimeError:
            # If no event loop is running in the current thread (e.g. CLI or sync context), run to completion
            asyncio.run(cls.broadcast_event_async(event))
