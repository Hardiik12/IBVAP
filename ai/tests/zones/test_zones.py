"""Unit tests for virtual polygon zone engine."""

import pytest

from ai.tracking.schemas import Track
from ai.zones.engine import PolygonZone, ZoneEngine, calculate_reference_point
from ai.zones.schemas import ZoneConfig, ZoneState


def test_calculate_reference_point() -> None:
    # Bounding box: [x1=100, y1=50, x2=200, y2=250]
    # Center X = (100+200)/2 = 150, Bottom Y = 250
    ref_pt = calculate_reference_point([100.0, 50.0, 200.0, 250.0])
    assert ref_pt == (150.0, 250.0)


def test_calculate_reference_point_invalid() -> None:
    with pytest.raises(ValueError, match="Expected 4 bounding box coordinates"):
        calculate_reference_point([100.0, 50.0])


def test_polygon_zone_direct_pixel_containment() -> None:
    # Square polygon from (100, 100) to (300, 300)
    config = ZoneConfig(
        zone_id="zone_01",
        name="Restricted Area",
        polygon_coordinates=[[100.0, 100.0], [300.0, 100.0], [300.0, 300.0], [100.0, 300.0]],
        is_normalized=False,
    )
    zone = PolygonZone(config)

    # Test point inside
    assert zone.contains_point((200.0, 200.0)) is True

    # Test point clearly outside
    assert zone.contains_point((50.0, 50.0)) is False
    assert zone.contains_point((400.0, 200.0)) is False

    # Test point on boundary / vertex
    assert zone.contains_point((100.0, 100.0)) is True
    assert zone.contains_point((200.0, 100.0)) is True


def test_polygon_zone_normalized_coordinates() -> None:
    # Normalized square [0.25, 0.25] to [0.75, 0.75]
    config = ZoneConfig(
        zone_id="zone_norm",
        name="Normalized Zone",
        polygon_coordinates=[[0.25, 0.25], [0.75, 0.25], [0.75, 0.75], [0.25, 0.75]],
        is_normalized=True,
    )
    # Frame resolution: 640x480 -> pixels [160, 120] to [480, 360]
    zone = PolygonZone(config, frame_resolution=(640, 480))

    # Point (320, 240) is dead center -> inside
    assert zone.contains_point((320.0, 240.0)) is True

    # Point (100, 100) is outside
    assert zone.contains_point((100.0, 100.0)) is False


def test_polygon_zone_non_convex_l_shape() -> None:
    # L-shaped polygon:
    # (0,0) -> (10,0) -> (10,5) -> (5,5) -> (5,10) -> (0,10)
    config = ZoneConfig(
        zone_id="zone_l",
        name="L-Zone",
        polygon_coordinates=[
            [0.0, 0.0],
            [10.0, 0.0],
            [10.0, 5.0],
            [5.0, 5.0],
            [5.0, 10.0],
            [0.0, 10.0],
        ],
        is_normalized=False,
    )
    zone = PolygonZone(config)

    # (2, 2) is inside the bottom bar
    assert zone.contains_point((2.0, 2.0)) is True

    # (2, 8) is inside the left vertical column
    assert zone.contains_point((2.0, 8.0)) is True

    # (8, 8) is in the empty cut-out area -> outside
    assert zone.contains_point((8.0, 8.0)) is False


def test_evaluate_track() -> None:
    config = ZoneConfig(
        zone_id="zone_01",
        name="Perimeter Fence",
        polygon_coordinates=[[100.0, 100.0], [400.0, 100.0], [400.0, 400.0], [100.0, 400.0]],
    )
    zone = PolygonZone(config)

    # Person with feet at (200, 250) -> INSIDE
    track_inside = Track(
        track_id=1,
        class_id=0,
        class_name="person",
        confidence=0.9,
        bbox=[150.0, 100.0, 250.0, 250.0],
    )
    assert zone.evaluate_track(track_inside) == ZoneState.INSIDE

    # Person with feet at (500, 550) -> OUTSIDE
    track_outside = Track(
        track_id=2,
        class_id=0,
        class_name="person",
        confidence=0.85,
        bbox=[450.0, 400.0, 550.0, 550.0],
    )
    assert zone.evaluate_track(track_outside) == ZoneState.OUTSIDE


def test_zone_engine_multiple_zones() -> None:
    zone_a = PolygonZone(
        ZoneConfig(
            zone_id="zone_a",
            name="Zone A",
            polygon_coordinates=[[0.0, 0.0], [100.0, 0.0], [100.0, 100.0], [0.0, 100.0]],
        )
    )
    zone_b = PolygonZone(
        ZoneConfig(
            zone_id="zone_b",
            name="Zone B",
            polygon_coordinates=[[200.0, 200.0], [300.0, 200.0], [300.0, 300.0], [200.0, 300.0]],
        )
    )
    engine = ZoneEngine([zone_a, zone_b])

    track_in_a = Track(
        track_id=10,
        class_id=0,
        class_name="person",
        confidence=0.9,
        bbox=[20.0, 10.0, 60.0, 50.0],  # feet at (40, 50) -> inside A
    )
    track_in_b = Track(
        track_id=20,
        class_id=0,
        class_name="person",
        confidence=0.9,
        bbox=[220.0, 210.0, 260.0, 250.0],  # feet at (240, 250) -> inside B
    )
    track_in_none = Track(
        track_id=30,
        class_id=0,
        class_name="person",
        confidence=0.9,
        bbox=[500.0, 500.0, 550.0, 550.0],  # outside both
    )

    results = engine.evaluate_tracks([track_in_a, track_in_b, track_in_none])

    assert len(results["zone_a"]) == 1
    assert results["zone_a"][0].track_id == 10

    assert len(results["zone_b"]) == 1
    assert results["zone_b"][0].track_id == 20
