import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from sqlalchemy import String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.enums import EventSeverity, AlertStatus

if TYPE_CHECKING:
    from app.models.event import Event
    from app.models.user import User


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("events.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    severity: Mapped[EventSeverity] = mapped_column(
        SQLEnum(EventSeverity), nullable=False, default=EventSeverity.HIGH
    )
    status: Mapped[AlertStatus] = mapped_column(
        SQLEnum(AlertStatus), nullable=False, default=AlertStatus.ACTIVE, index=True
    )
    message: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    acknowledged_by: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)

    # Relationships
    event: Mapped["Event"] = relationship("Event", back_populates="alert")
    acknowledged_by_user: Mapped[Optional["User"]] = relationship("User", back_populates="acknowledged_alerts")

    def __repr__(self) -> str:
        return f"<Alert id={self.id} event_id={self.event_id} status={self.status}>"
