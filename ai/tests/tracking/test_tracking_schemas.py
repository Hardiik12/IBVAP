"""Unit tests for tracking schemas and spatial reference point math."""

from ai.tracking.schemas import Track


def test_track_reference_point_auto_calculation() -> None:
    # Bounding box: [x1=100.0, y1=200.0, x2=300.0, y2=600.0]
    # Expected reference point: ((100 + 300) / 2, 600) = (200.0, 600.0)
    track = Track(
        track_id=1,
        class_id=0,
        class_name="person",
        confidence=0.91,
        bbox=[100.0, 200.0, 300.0, 600.0],
    )
    assert track.reference_point == (200.0, 600.0)
    assert track.current_zone_state == "OUTSIDE"


def test_track_to_dict() -> None:
    track = Track(
        track_id=42,
        class_id=2,
        class_name="car",
        confidence=0.87,
        bbox=[50.0, 80.0, 250.0, 300.0],
        current_zone_state="INSIDE",
    )
    data = track.to_dict()
    assert data["track_id"] == 42
    assert data["class_id"] == 2
    assert data["class_name"] == "car"
    assert data["confidence"] == 0.87
    assert data["bbox"] == [50.0, 80.0, 250.0, 300.0]
    assert data["reference_point"] == [150.0, 300.0]
    assert data["current_zone_state"] == "INSIDE"
    assert "last_updated" in data
