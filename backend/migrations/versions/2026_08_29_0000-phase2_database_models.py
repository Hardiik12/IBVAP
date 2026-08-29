"""Phase 2 Database Models (Camera, Zone, Event, Alert, Evidence, User, AuditLog)

Revision ID: phase2_database_models
Revises: 
Create Date: 2026-08-29 20:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "phase2_database_models"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. users
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("email", sa.String(length=100), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column(
            "role",
            sa.Enum("OPERATOR", "ANALYST", "ADMINISTRATOR", "AUDITOR", name="userrole"),
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    # 2. cameras
    op.create_table(
        "cameras",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("camera_identifier", sa.String(length=50), nullable=False),
        sa.Column(
            "source_type",
            sa.Enum("WEBCAM", "VIDEO_FILE", "RTSP", name="camerasourcetype"),
            nullable=False,
        ),
        sa.Column("source_url", sa.String(length=255), nullable=True),
        sa.Column("location", sa.String(length=100), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_cameras_camera_identifier"), "cameras", ["camera_identifier"], unique=True)

    # 3. zones
    op.create_table(
        "zones",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("camera_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column(
            "zone_type",
            sa.Enum("RESTRICTED", "MONITORED", name="zonetype"),
            nullable=False,
        ),
        sa.Column("polygon_coordinates", sa.JSON(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["camera_id"], ["cameras.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_zones_camera_id"), "zones", ["camera_id"], unique=False)

    # 4. events
    op.create_table(
        "events",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("event_identifier", sa.String(length=50), nullable=False),
        sa.Column(
            "event_type",
            sa.Enum("INTRUSION", "EXIT", "LOITERING", "UNAUTHORIZED_VEHICLE", name="eventtype"),
            nullable=False,
        ),
        sa.Column("camera_id", sa.String(length=36), nullable=False),
        sa.Column("zone_id", sa.String(length=36), nullable=True),
        sa.Column("track_id", sa.Integer(), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "severity",
            sa.Enum("LOW", "MEDIUM", "HIGH", "CRITICAL", name="eventseverity"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum("NEW", "PROCESSED", "ARCHIVED", name="eventstatus"),
            nullable=False,
        ),
        sa.Column("bounding_box", sa.JSON(), nullable=True),
        sa.Column("position", sa.JSON(), nullable=True),
        sa.Column("event_metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["camera_id"], ["cameras.id"]),
        sa.ForeignKeyConstraint(["zone_id"], ["zones.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_events_event_identifier"), "events", ["event_identifier"], unique=True)
    op.create_index(op.f("ix_events_event_type"), "events", ["event_type"], unique=False)
    op.create_index(op.f("ix_events_camera_id"), "events", ["camera_id"], unique=False)
    op.create_index(op.f("ix_events_zone_id"), "events", ["zone_id"], unique=False)
    op.create_index(op.f("ix_events_timestamp"), "events", ["timestamp"], unique=False)
    op.create_index("idx_events_camera_timestamp", "events", ["camera_id", "timestamp"])

    # 5. alerts
    op.create_table(
        "alerts",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("event_id", sa.String(length=36), nullable=False),
        sa.Column(
            "severity",
            sa.Enum("LOW", "MEDIUM", "HIGH", "CRITICAL", name="eventseverity"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum("ACTIVE", "ACKNOWLEDGED", "RESOLVED", name="alertstatus"),
            nullable=False,
        ),
        sa.Column("message", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("acknowledged_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("acknowledged_by", sa.String(length=36), nullable=True),
        sa.ForeignKeyConstraint(["event_id"], ["events.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["acknowledged_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("event_id"),
    )
    op.create_index(op.f("ix_alerts_event_id"), "alerts", ["event_id"], unique=True)
    op.create_index(op.f("ix_alerts_status"), "alerts", ["status"], unique=False)

    # 6. evidence
    op.create_table(
        "evidence",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("evidence_identifier", sa.String(length=50), nullable=False),
        sa.Column("event_id", sa.String(length=36), nullable=False),
        sa.Column("file_path", sa.String(length=255), nullable=False),
        sa.Column("sha256_hash", sa.String(length=64), nullable=False),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("evidence_metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["event_id"], ["events.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_evidence_evidence_identifier"), "evidence", ["evidence_identifier"], unique=True)
    op.create_index(op.f("ix_evidence_event_id"), "evidence", ["event_id"], unique=False)
    op.create_index(op.f("ix_evidence_sha256_hash"), "evidence", ["sha256_hash"], unique=False)

    # 7. audit_logs
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("resource_type", sa.String(length=50), nullable=False),
        sa.Column("resource_id", sa.String(length=50), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("log_metadata", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_audit_logs_user_id"), "audit_logs", ["user_id"], unique=False)
    op.create_index(op.f("ix_audit_logs_timestamp"), "audit_logs", ["timestamp"], unique=False)


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("evidence")
    op.drop_table("alerts")
    op.drop_table("events")
    op.drop_table("zones")
    op.drop_table("cameras")
    op.drop_table("users")
