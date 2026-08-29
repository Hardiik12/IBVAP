import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional, List, Any
from sqlalchemy import String, Integer, DateTime, ForeignKey, JSON, Enum as SQLEnum, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.enums import EventType, EventSeverity, EventStatus

if TYPE_CHECKING:
    from app.models.camera import Camera
    from app.models.zone import Zone
    from app.models.alert import Alert
    from app.models.evidence import Evidence


class Event(Base):
    __tablename__ = "events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_identifier: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    event_type: Mapped[EventType] = mapped_column(
        SQLEnum(EventType), nullable=False, default=EventType.INTRUSION, index=True
    )
    camera_id: Mapped[str] = mapped_column(String(36), ForeignKey("cameras.id"), nullable=False, index=True)
    zone_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("zones.id"), nullable=True, index=True)
    track_id: Mapped[int] = mapped_column(Integer, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )
    severity: Mapped[EventSeverity] = mapped_column(
        SQLEnum(EventSeverity), nullable=False, default=EventSeverity.HIGH
    )
    status: Mapped[EventStatus] = mapped_column(
        SQLEnum(EventStatus), nullable=False, default=EventStatus.NEW
    )
    bounding_box: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    position: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    event_metadata: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    camera: Mapped["Camera"] = relationship("Camera", back_populates="events")
    zone: Mapped[Optional["Zone"]] = relationship("Zone", back_populates="events")
    alert: Mapped[Optional["Alert"]] = relationship("Alert", back_populates="event", uselist=False)
    evidence: Mapped[List["Evidence"]] = relationship("Evidence", back_populates="event")

    __table_args__ = (
        Index("idx_events_camera_timestamp", "camera_id", "timestamp"),
    )

    def __repr__(self) -> str:
        return f"<Event id={self.id} identifier={self.event_identifier} type={self.event_type}>"
