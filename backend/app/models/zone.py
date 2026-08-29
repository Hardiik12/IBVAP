import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Any
from sqlalchemy import String, Boolean, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.enums import ZoneType

if TYPE_CHECKING:
    from app.models.camera import Camera
    from app.models.event import Event


class Zone(Base):
    __tablename__ = "zones"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    camera_id: Mapped[str] = mapped_column(String(36), ForeignKey("cameras.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    zone_type: Mapped[ZoneType] = mapped_column(
        SQLEnum(ZoneType), nullable=False, default=ZoneType.RESTRICTED
    )
    # Stored as list of 2D normalized coordinates [[x1, y1], [x2, y2], ...]
    polygon_coordinates: Mapped[Any] = mapped_column(JSON, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    camera: Mapped["Camera"] = relationship("Camera", back_populates="zones")
    events: Mapped[List["Event"]] = relationship("Event", back_populates="zone")

    def __repr__(self) -> str:
        return f"<Zone id={self.id} name={self.name} camera_id={self.camera_id}>"
