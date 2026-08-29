"""Unit tests for AIPipeline orchestrator."""

from unittest.mock import MagicMock

import numpy as np

from ai.events.engine import IntrusionEventEngine
from ai.pipeline.runner import AIPipeline
from ai.tracking.schemas import Track
from ai.zones.engine import PolygonZone, ZoneEngine
from ai.zones.schemas import ZoneConfig


def test_pipeline_end_to_end_flow() -> None:
    # 1. Setup mock tracker
    mock_tracker = MagicMock()

    # Track outside in frame 1, inside in frame 2
    track_outside = Track(
        track_id=10,
        class_id=0,
        class_name="person",
        confidence=0.92,
        bbox=[10.0, 10.0, 50.0, 50.0],
    )
    track_inside = Track(
        track_id=10,
        class_id=0,
        class_name="person",
        confidence=0.92,
        bbox=[150.0, 150.0, 250.0, 250.0],  # feet at (200, 250) -> inside zone
    )

    # 2. Setup zone engine
    zone_config = ZoneConfig(
        zone_id="perimeter_01",
        name="Border Zone",
        polygon_coordinates=[
            [100.0, 100.0],
            [300.0, 100.0],
            [300.0, 300.0],
            [100.0, 300.0],
        ],
    )
    zone_engine = ZoneEngine([PolygonZone(zone_config)])
    event_engine = IntrusionEventEngine(default_camera_id="cam-01")

    pipeline = AIPipeline(
        tracker=mock_tracker,
        zone_engine=zone_engine,
        event_engine=event_engine,
        camera_id="cam-01",
    )

    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)

    # Frame 1: Track outside -> 0 events
    mock_tracker.track.return_value = [track_outside]
    res1 = pipeline.process_frame(dummy_frame)
    assert len(res1.events) == 0
    assert len(res1.tracks) == 1
    assert res1.latency_ms >= 0.0

    # Frame 2: Track enters zone -> 1 event
    mock_tracker.track.return_value = [track_inside]
    res2 = pipeline.process_frame(dummy_frame, capture_snapshot=True)
    assert len(res2.events) == 1
    assert res2.events[0].track_id == 10
    assert res2.events[0].zone_id == "perimeter_01"
    assert res2.events[0].evidence_snapshot is not None

    # Frame 3: Track remains inside zone -> 0 events (alert suppression)
    mock_tracker.track.return_value = [track_inside]
    res3 = pipeline.process_frame(dummy_frame)
    assert len(res3.events) == 0


def test_pipeline_reset() -> None:
    mock_tracker = MagicMock()
    mock_event_engine = MagicMock()
    pipeline = AIPipeline(
        tracker=mock_tracker,
        event_engine=mock_event_engine,
    )
    pipeline.reset()
    mock_tracker.reset.assert_called_once()
    mock_event_engine.reset_zone_states.assert_called_once()
