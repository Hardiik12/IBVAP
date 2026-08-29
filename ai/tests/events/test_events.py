"""Unit tests for intrusion event engine and state transitions."""

import numpy as np

from ai.events.engine import IntrusionEventEngine, encode_frame_to_base64
from ai.events.schemas import EventPayload, EventType, Severity
from ai.tracking.schemas import Track
from ai.zones.engine import PolygonZone
from ai.zones.schemas import ZoneConfig


def create_test_zone(zone_id: str = "zone-01") -> PolygonZone:
    """Helper to create a test square polygon from (100, 100) to (300, 300)."""
    config = ZoneConfig(
        zone_id=zone_id,
        name="Test Restricted Zone",
        polygon_coordinates=[
            [100.0, 100.0],
            [300.0, 100.0],
            [300.0, 300.0],
            [100.0, 300.0],
        ],
    )
    return PolygonZone(config)


def test_event_payload_serialization() -> None:
    payload = EventPayload(
        camera_id="cam-01",
        zone_id="zone-01",
        track_id=7,
        class_name="person",
        confidence=0.94231,
        bbox=[120.0, 150.0, 220.0, 290.0],
        event_type=EventType.INTRUSION.value,
        severity=Severity.HIGH.value,
        timestamp="2026-08-29T18:00:00Z",
    )
    data = payload.to_dict()
    assert data["camera_id"] == "cam-01"
    assert data["zone_id"] == "zone-01"
    assert data["track_id"] == 7
    assert data["class_name"] == "person"
    assert data["confidence"] == 0.9423
    assert data["severity"] == "HIGH"
    assert data["bbox"] == [120.0, 150.0, 220.0, 290.0]
    assert "evidence_snapshot" not in data


def test_encode_frame_to_base64() -> None:
    dummy_frame = np.zeros((100, 100, 3), dtype=np.uint8)
    b64_str = encode_frame_to_base64(dummy_frame)
    assert isinstance(b64_str, str)
    assert len(b64_str) > 50


def test_state_transition_single_entry_and_suppression() -> None:
    """Verify that entering generates 1 event and staying inside generates 0 extra events."""
    engine = IntrusionEventEngine(default_camera_id="cam-01")
    zone = create_test_zone("zone-01")

    # Frame 1: Person outside at (50, 50)
    track_outside = Track(
        track_id=1,
        class_id=0,
        class_name="person",
        confidence=0.90,
        bbox=[20.0, 10.0, 80.0, 50.0],  # feet at (50, 50)
    )
    events_f1 = engine.process_tracks(zone, [track_outside])
    assert len(events_f1) == 0

    # Frame 2: Person enters restricted zone at (200, 200) -> OUTSIDE -> INSIDE (TRIGGER)
    track_inside = Track(
        track_id=1,
        class_id=0,
        class_name="person",
        confidence=0.92,
        bbox=[150.0, 100.0, 250.0, 200.0],  # feet at (200, 200)
    )
    events_f2 = engine.process_tracks(zone, [track_inside])
    assert len(events_f2) == 1
    event = events_f2[0]
    assert event.track_id == 1
    assert event.class_name == "person"
    assert event.severity == Severity.HIGH.value
    assert event.event_type == EventType.INTRUSION.value
    assert track_inside.current_zone_state == "INSIDE"

    # Frames 3 to 10: Person remains inside -> INSIDE -> INSIDE (SUPPRESSION)
    for _ in range(8):
        events_fn = engine.process_tracks(zone, [track_inside])
        assert len(events_fn) == 0, "Duplicate event emitted while subject remained inside zone!"


def test_state_transition_exit_and_reentry() -> None:
    """Verify that exiting and re-entering triggers a new event on second entry."""
    engine = IntrusionEventEngine(default_camera_id="cam-01")
    zone = create_test_zone("zone-01")

    track_inside = Track(
        track_id=5,
        class_id=0,
        class_name="person",
        confidence=0.88,
        bbox=[150.0, 100.0, 250.0, 200.0],
    )
    track_outside = Track(
        track_id=5,
        class_id=0,
        class_name="person",
        confidence=0.88,
        bbox=[20.0, 10.0, 80.0, 50.0],
    )

    # 1. Enter zone -> Trigger event 1
    events1 = engine.process_tracks(zone, [track_inside])
    assert len(events1) == 1

    # 2. Exit zone -> Reset state to OUTSIDE, no event
    events2 = engine.process_tracks(zone, [track_outside])
    assert len(events2) == 0
    assert track_outside.current_zone_state == "OUTSIDE"

    # 3. Re-enter zone -> Trigger event 2
    events3 = engine.process_tracks(zone, [track_inside])
    assert len(events3) == 1
    assert events3[0].track_id == 5


def test_multiple_tracks_independent_evaluation() -> None:
    engine = IntrusionEventEngine(default_camera_id="cam-01")
    zone = create_test_zone("zone-01")

    track_1 = Track(
        track_id=10,
        class_id=0,
        class_name="person",
        confidence=0.90,
        bbox=[150.0, 100.0, 250.0, 200.0],  # INSIDE
    )
    track_2 = Track(
        track_id=20,
        class_id=7,
        class_name="truck",
        confidence=0.95,
        bbox=[150.0, 100.0, 250.0, 200.0],  # INSIDE
    )

    events = engine.process_tracks(zone, [track_1, track_2])
    assert len(events) == 2

    # Track 10 is person -> HIGH
    evt_person = next(e for e in events if e.track_id == 10)
    assert evt_person.severity == Severity.HIGH.value

    # Track 20 is truck -> CRITICAL
    evt_truck = next(e for e in events if e.track_id == 20)
    assert evt_truck.severity == Severity.CRITICAL.value


def test_snapshot_capture_inclusion() -> None:
    engine = IntrusionEventEngine(default_camera_id="cam-01")
    zone = create_test_zone("zone-01")

    track = Track(
        track_id=99,
        class_id=0,
        class_name="person",
        confidence=0.90,
        bbox=[150.0, 100.0, 250.0, 200.0],
    )
    dummy_frame = np.zeros((240, 320, 3), dtype=np.uint8)

    events = engine.process_tracks(
        zone=zone,
        tracks=[track],
        frame=dummy_frame,
        capture_snapshot=True,
    )
    assert len(events) == 1
    assert events[0].evidence_snapshot is not None
    assert len(events[0].evidence_snapshot) > 50


def test_stale_track_cleanup() -> None:
    engine = IntrusionEventEngine()
    zone = create_test_zone("zone-01")

    track = Track(
        track_id=33,
        class_id=0,
        class_name="person",
        confidence=0.90,
        bbox=[150.0, 100.0, 250.0, 200.0],
    )
    engine.process_tracks(zone, [track])
    assert len(engine._track_states) == 1

    # Cleanup with 0 idle seconds should purge immediately
    purged = engine.cleanup_stale_tracks(max_idle_seconds=-1.0)
    assert purged == 1
    assert len(engine._track_states) == 0
