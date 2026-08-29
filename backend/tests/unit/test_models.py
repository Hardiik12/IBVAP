import pytest
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.models.camera import Camera
from app.models.zone import Zone
from app.models.event import Event
from app.models.alert import Alert
from app.models.evidence import Evidence
from app.models.user import User
from app.models.audit_log import AuditLog
from app.models.enums import (
    CameraSourceType,
    ZoneType,
    EventType,
    EventSeverity,
    EventStatus,
    AlertStatus,
    UserRole,
)


def test_create_camera_and_unique_constraint(db_session: Session) -> None:
    """
    Test 1: Create Camera & enforce unique camera_identifier constraint.
    """
    cam1 = Camera(
        name="Camera 1",
        camera_identifier="cam-01",
        source_type=CameraSourceType.WEBCAM,
        location="Zone Alpha"
    )
    db_session.add(cam1)
    db_session.commit()

    assert cam1.id is not None
    assert cam1.camera_identifier == "cam-01"

    # Attempt to insert duplicate identifier
    cam2 = Camera(
        name="Camera Duplicate",
        camera_identifier="cam-01",
        source_type=CameraSourceType.RTSP
    )
    db_session.add(cam2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_create_zone_linked_to_camera(db_session: Session) -> None:
    """
    Test 2: Create Zone linked to Camera & verify polygon JSON storage.
    """
    cam = Camera(name="Cam Zone Test", camera_identifier="cam-zone-01")
    db_session.add(cam)
    db_session.commit()

    polygon = [[0.1, 0.2], [0.8, 0.2], [0.8, 0.9], [0.1, 0.9]]
    zone = Zone(
        camera_id=cam.id,
        name="Restricted Area",
        zone_type=ZoneType.RESTRICTED,
        polygon_coordinates=polygon
    )
    db_session.add(zone)
    db_session.commit()

    assert zone.id is not None
    assert zone.camera_id == cam.id
    assert zone.polygon_coordinates == polygon
    assert len(cam.zones) == 1
    assert cam.zones[0].name == "Restricted Area"


def test_create_event(db_session: Session) -> None:
    """
    Test 3: Create Event linked to Camera & Zone with unique event_identifier.
    """
    cam = Camera(name="Cam Event Test", camera_identifier="cam-evt-01")
    db_session.add(cam)
    db_session.commit()

    zone = Zone(camera_id=cam.id, name="Test Zone", polygon_coordinates=[[0, 0], [1, 1]])
    db_session.add(zone)
    db_session.commit()

    event = Event(
        event_identifier="evt-1001",
        event_type=EventType.INTRUSION,
        camera_id=cam.id,
        zone_id=zone.id,
        track_id=17,
        severity=EventSeverity.HIGH,
        status=EventStatus.NEW
    )
    db_session.add(event)
    db_session.commit()

    assert event.id is not None
    assert event.event_identifier == "evt-1001"
    assert event.track_id == 17
    assert event.camera.camera_identifier == "cam-evt-01"
    assert event.zone.name == "Test Zone"


def test_create_alert_linked_to_event(db_session: Session) -> None:
    """
    Test 4: Create Alert linked to Event (1:1 relationship).
    """
    cam = Camera(name="Cam Alert Test", camera_identifier="cam-alt-01")
    db_session.add(cam)
    db_session.commit()

    event = Event(
        event_identifier="evt-2001",
        event_type=EventType.INTRUSION,
        camera_id=cam.id,
        track_id=42
    )
    db_session.add(event)
    db_session.commit()

    alert = Alert(
        event_id=event.id,
        severity=EventSeverity.CRITICAL,
        status=AlertStatus.ACTIVE,
        message="Unauthorized perimeter entry detected"
    )
    db_session.add(alert)
    db_session.commit()

    assert alert.id is not None
    assert alert.event_id == event.id
    assert event.alert.message == "Unauthorized perimeter entry detected"


def test_create_evidence(db_session: Session) -> None:
    """
    Test 5: Create Evidence linked to Event with SHA-256 metadata field.
    """
    cam = Camera(name="Cam Evidence Test", camera_identifier="cam-evi-01")
    db_session.add(cam)
    db_session.commit()

    event = Event(
        event_identifier="evt-3001",
        event_type=EventType.INTRUSION,
        camera_id=cam.id,
        track_id=99
    )
    db_session.add(event)
    db_session.commit()

    hash_val = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    evidence = Evidence(
        evidence_identifier="evi-5001",
        event_id=event.id,
        file_path="/data/evidence/evi-5001.jpg",
        sha256_hash=hash_val,
        captured_at=datetime.now(timezone.utc)
    )
    db_session.add(evidence)
    db_session.commit()

    assert evidence.id is not None
    assert evidence.evidence_identifier == "evi-5001"
    assert evidence.sha256_hash == hash_val
    assert evidence.event.event_identifier == "evt-3001"


def test_user_creation_and_role_validation(db_session: Session) -> None:
    """
    Test 6: User model role validation & password_hash field existence.
    """
    user = User(
        username="operator_bob",
        email="bob@ibvap.local",
        password_hash="$2b$12$fakehashedpasswordhash12345",
        role=UserRole.OPERATOR
    )
    db_session.add(user)
    db_session.commit()

    assert user.id is not None
    assert user.username == "operator_bob"
    assert user.role == UserRole.OPERATOR
    assert hasattr(user, "password_hash")
    assert not hasattr(user, "password")


def test_audit_log(db_session: Session) -> None:
    """
    Test 7: Create AuditLog referencing User.
    """
    user = User(
        username="admin_user",
        email="admin@ibvap.local",
        password_hash="$2b$12$fakehash",
        role=UserRole.ADMINISTRATOR
    )
    db_session.add(user)
    db_session.commit()

    audit = AuditLog(
        user_id=user.id,
        action="VERIFY_EVIDENCE",
        resource_type="EVIDENCE",
        resource_id="evi-5001",
        log_metadata={"status": "VERIFIED"}
    )
    db_session.add(audit)
    db_session.commit()

    assert audit.id is not None
    assert audit.user_id == user.id
    assert audit.user.username == "admin_user"
    assert audit.action == "VERIFY_EVIDENCE"
