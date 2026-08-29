import os
import uuid
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from app.core.logging import logger
from app.db.database import SessionLocal
from app.models.camera import Camera
from app.models.zone import Zone
from app.models.user import User
from app.models.event import Event
from app.models.alert import Alert
from app.models.evidence import Evidence
from app.models.enums import CameraSourceType, ZoneType, UserRole, EventType, EventSeverity, EventStatus, AlertStatus
from app.core.security import hash_password


def seed_demo_data(db: Session) -> None:
    """
    Seeds development-only demo records into database.
    Creates demo camera, restricted zone, security users, events, alerts, and evidence.
    """
    logger.info("Checking for demo seed data...")

    # Development operator credentials from environment or defaults
    dev_admin_user = os.environ.get("DEV_ADMIN_USERNAME", "admin")
    dev_admin_pass = os.environ.get("DEV_ADMIN_PASSWORD", "Admin@123")

    # 1. Seed Demo Admin Users
    seed_users = [
        (dev_admin_user, f"{dev_admin_user}@ibvap.local", dev_admin_pass, UserRole.ADMINISTRATOR),
        ("admin_user", "admin_user@ibvap.local", "AdminSecret123!", UserRole.ADMINISTRATOR),
        ("operator_01", "operator01@ibvap.local", "Operator@123", UserRole.OPERATOR),
    ]

    for uname, uemail, upass, urole in seed_users:
        user = db.query(User).filter(User.username == uname).first()
        if not user:
            user = User(
                username=uname,
                email=uemail,
                password_hash=hash_password(upass),
                role=urole,
                is_active=True,
                mfa_enabled=False,
            )
            db.add(user)
            logger.info(f"Seeded development user ('{uname}').")
        else:
            user.password_hash = hash_password(upass)

    # 2. Seed Demo Camera
    camera = db.query(Camera).filter(Camera.camera_identifier == "cam-webcam-01").first()
    if not camera:
        camera = Camera(
            name="Main Perimeter Webcam 01",
            camera_identifier="cam-webcam-01",
            source_type=CameraSourceType.WEBCAM,
            source_url="0",
            location="Gate Alpha Perimeter",
            is_active=True,
        )
        db.add(camera)
        db.flush()
        logger.info("Seeded development camera ('cam-webcam-01').")

    # 3. Seed Demo Zone
    zone = db.query(Zone).filter(Zone.name == "Perimeter Restricted Zone A").first()
    if not zone:
        zone = Zone(
            camera_id=camera.id,
            name="Perimeter Restricted Zone A",
            zone_type=ZoneType.RESTRICTED,
            polygon_coordinates=[
                [0.20, 0.30],
                [0.80, 0.30],
                [0.85, 0.85],
                [0.15, 0.85],
            ],
            is_active=True,
        )
        db.add(zone)
        db.flush()
        logger.info("Seeded development restricted zone ('Perimeter Restricted Zone A').")

    # 4. Seed Demo Events, Alerts, & Evidence (if none exist)
    existing_event = db.query(Event).first()
    if not existing_event:
        now = datetime.now(timezone.utc)

        # Event 1: Intrusion Breach
        ev1 = Event(
            id="evt-demo-001",
            event_identifier="EVT-20260830-001",
            event_type=EventType.INTRUSION,
            camera_id=camera.id,
            zone_id=zone.id,
            track_id=1,
            timestamp=now - timedelta(minutes=4),
            severity=EventSeverity.CRITICAL,
            status=EventStatus.NEW,
            bounding_box=[0.42, 0.35, 0.58, 0.65],
            position=[0.50, 0.65],
            event_metadata={"confidence": 0.94, "class": "person", "speed_kmh": 6.2},
        )
        db.add(ev1)
        db.flush()

        # Alert 1
        al1 = Alert(
            id="alt-demo-001",
            event_id=ev1.id,
            status=AlertStatus.ACTIVE,
        )
        db.add(al1)

        # Evidence 1
        evd1 = Evidence(
            id="evi-demo-001",
            evidence_identifier="EVD-20260830-001",
            event_id=ev1.id,
            file_path="sim_frame_demo_01.jpg",
            sha256_hash="5e02e28396de63568f5aba8333e4cae1c25d4b37255edb06d3de795c21b3a730",
            captured_at=now - timedelta(minutes=4),
            evidence_metadata={"camera_resolution": "1920x1080", "yolo_model": "YOLOv8n"},
        )
        db.add(evd1)

        # Event 2: Vehicle Loitering
        ev2 = Event(
            id="evt-demo-002",
            event_identifier="EVT-20260830-002",
            event_type=EventType.UNAUTHORIZED_VEHICLE,
            camera_id=camera.id,
            zone_id=zone.id,
            track_id=4,
            timestamp=now - timedelta(minutes=12),
            severity=EventSeverity.HIGH,
            status=EventStatus.PROCESSED,
            bounding_box=[0.25, 0.40, 0.45, 0.70],
            position=[0.35, 0.70],
            event_metadata={"confidence": 0.88, "class": "vehicle", "dwell_time_sec": 45},
        )
        db.add(ev2)
        db.flush()

        al2 = Alert(
            id="alt-demo-002",
            event_id=ev2.id,
            status=AlertStatus.ACKNOWLEDGED,
        )
        db.add(al2)

        evd2 = Evidence(
            id="evi-demo-002",
            evidence_identifier="EVD-20260830-002",
            event_id=ev2.id,
            file_path="sim_frame_demo_02.jpg",
            sha256_hash="9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
            captured_at=now - timedelta(minutes=12),
            evidence_metadata={"camera_resolution": "1920x1080", "yolo_model": "YOLOv8n"},
        )
        db.add(evd2)
        logger.info("Seeded demo events, alerts, and evidence snapshots.")

    db.commit()
    logger.info("Demo seed data process complete.")


if __name__ == "__main__":
    db_session = SessionLocal()
    try:
        seed_demo_data(db_session)
    finally:
        db_session.close()
