"""End-to-end AI analytics pipeline orchestrator for IBVAP."""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import numpy as np

from ai.events.engine import IntrusionEventEngine
from ai.events.schemas import EventPayload
from ai.tracking.schemas import Track
from ai.tracking.tracker import ByteTracker
from ai.zones.engine import ZoneEngine


@dataclass
class PipelineResult:
    """Output generated from processing a single video frame through the AI pipeline."""

    frame: np.ndarray
    tracks: list[Track]
    events: list[EventPayload]
    fps: float = 0.0
    latency_ms: float = 0.0
    metadata: dict = field(default_factory=dict)


class AIPipeline:
    """
    Unified AI pipeline orchestrating:
    Frame -> ByteTracker (Detection+Tracking) -> ZoneEngine -> IntrusionEventEngine -> Events.
    """

    def __init__(
        self,
        tracker: ByteTracker | None = None,
        zone_engine: ZoneEngine | None = None,
        event_engine: IntrusionEventEngine | None = None,
        camera_id: str = "cam-01",
    ) -> None:
        self.camera_id = camera_id
        self.tracker = tracker or ByteTracker()
        self.zone_engine = zone_engine or ZoneEngine()
        self.event_engine = event_engine or IntrusionEventEngine(default_camera_id=camera_id)

        self._frame_count = 0
        self._fps_start_time = time.perf_counter()
        self._current_fps = 0.0

    def process_frame(
        self,
        frame: np.ndarray,
        capture_snapshot: bool = True,
    ) -> PipelineResult:
        """
        Process a single BGR video frame through the full analytics pipeline.

        1. Track objects across frames (ByteTrack)
        2. Evaluate containment against registered polygon zones
        3. Trigger intrusion events on positive transitions
        """
        t0 = time.perf_counter()

        # Step 1: Detect and Track
        tracks = self.tracker.track(frame)

        # Step 2 & 3: Evaluate each registered zone for intrusions
        triggered_events: list[EventPayload] = []
        for zone in self.zone_engine.zones:
            events = self.event_engine.process_tracks(
                zone=zone,
                tracks=tracks,
                camera_id=self.camera_id,
                frame=frame,
                capture_snapshot=capture_snapshot,
            )
            triggered_events.extend(events)

        t1 = time.perf_counter()
        latency_ms = (t1 - t0) * 1000.0

        # Update FPS calculation
        self._frame_count += 1
        elapsed = t1 - self._fps_start_time
        if elapsed >= 1.0:
            self._current_fps = self._frame_count / elapsed
            self._frame_count = 0
            self._fps_start_time = t1

        return PipelineResult(
            frame=frame,
            tracks=tracks,
            events=triggered_events,
            fps=self._current_fps,
            latency_ms=latency_ms,
        )

    def reset(self) -> None:
        """Reset internal tracker and event states."""
        self.tracker.reset()
        self.event_engine.reset_zone_states()
