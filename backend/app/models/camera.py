import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.enums import CameraSourceType

if TYPE_CHECKING:
    from app.models.zone import Zone
    from app.models.event import Event


class Camera(Base):
    __tablename__ = "cameras"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    camera_identifier: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    source_type: Mapped[CameraSourceType] = mapped_column(
        SQLEnum(CameraSourceType), nullable=False, default=CameraSourceType.WEBCAM
    )
    source_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
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
    zones: Mapped[List["Zone"]] = relationship("Zone", back_populates="camera", cascade="all, delete-orphan")
    events: Mapped[List["Event"]] = relationship("Event", back_populates="camera")

    def __repr__(self) -> str:
        return f"<Camera id={self.id} identifier={self.camera_identifier} type={self.source_type}>"
