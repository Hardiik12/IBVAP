"""
Intrusion Event Engine for state transition evaluation and alert generation.

M2 Ownership Scope:
- Evaluates OUTSIDE -> INSIDE state transitions per tracked object.
- Suppresses duplicate alert spam while subject remains INSIDE (ADR-007).
- Resets tracking state upon INSIDE -> OUTSIDE transition.
- Emits standardized EventPayload instances to downstream consumers.

Downstream Handlers (M5 / Phase 7 & 8):
- Evidence file persistence to disk, SHA-256 hash digest calculation,
  and database storage are handled downstream by M5 services.
"""

from __future__ import annotations

import base64
import time
from datetime import datetime, timezone

import cv2
import numpy as np

from ai.events.schemas import EventPayload, EventType, Severity
from ai.tracking.schemas import Track
from ai.zones.engine import PolygonZone
from ai.zones.schemas import ZoneState


def encode_frame_to_base64(frame: np.ndarray, quality: int = 85) -> str:
    """
    Encode an OpenCV BGR frame into a base64 JPEG string.

    Transport Helper: Provides in-memory JPEG string for optional inclusion in
    the event payload. Evidence file writing to disk and cryptographic SHA-256
    integrity verification are performed downstream by M5 (Phase 7 & 8).
    """
    encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    success, buffer = cv2.imencode(".jpg", frame, encode_params)
    if not success:
        raise ValueError("Failed to encode frame to JPEG format.")
    return base64.b64encode(buffer).decode("utf-8")


class IntrusionEventEngine:
    """
    Evaluates track state transitions across virtual zones and generates security events.

    Duplicate Suppression (ADR-007):
    - Evaluates OUTSIDE -> INSIDE state transitions per (zone_id, track_id).
    - Emits exactly ONE event upon the initial entry edge (positive transition).
    - Consecutive INSIDE -> INSIDE evaluations produce 0 duplicate events.
    - An INSIDE -> OUTSIDE transition resets the state to OUTSIDE, enabling
      a new event if the subject exits and re-enters.
    """

    def __init__(self, default_camera_id: str = "cam-01") -> None:
        self.default_camera_id = default_camera_id
        # Key: (zone_id, track_id) -> ZoneState
        self._track_states: dict[tuple[str, int], ZoneState] = {}
        # Key: (zone_id, track_id) -> last seen timestamp in epoch seconds (for stale track cleanup)
        self._last_seen: dict[tuple[str, int], float] = {}

    def _determine_severity(self, class_name: str) -> str:
        """Assign severity level based on detected object class."""
        if class_name in {"truck", "bus", "car"}:
            return Severity.CRITICAL.value
        return Severity.HIGH.value

    def process_tracks(
        self,
        zone: PolygonZone,
        tracks: list[Track],
        camera_id: str | None = None,
        frame: np.ndarray | None = None,
        capture_snapshot: bool = False,
    ) -> list[EventPayload]:
        """
        Process active tracks against a polygon zone and return newly triggered events.

        :param zone: Target PolygonZone to evaluate tracks against.
        :param tracks: List of active Track instances from the tracking module.
        :param camera_id: Camera identifier (defaults to self.default_camera_id).
        :param frame: Optional BGR frame numpy array for evidence snapshot capture.
        :param capture_snapshot: Whether to encode a JPEG snapshot for emitted events.
        :return: List of EventPayload instances for positive edge transitions (OUTSIDE -> INSIDE).
        """
        cam_id = camera_id or self.default_camera_id
        zone_id = zone.config.zone_id
        now_ts = time.time()
        emitted_events: list[EventPayload] = []

        # Snapshot base64 string cached for the frame if needed
        encoded_snapshot: str | None = None
        if capture_snapshot and frame is not None:
            encoded_snapshot = encode_frame_to_base64(frame)

        for track in tracks:
            # Skip invalid / unassigned track IDs
            if track.track_id < 0:
                continue

            state_key = (zone_id, track.track_id)
            prev_state = self._track_states.get(state_key, ZoneState.OUTSIDE)
            current_state = zone.evaluate_track(track)

            # Update track dataclass state
            track.current_zone_state = current_state.value
            self._last_seen[state_key] = now_ts

            # Check for positive state transition: OUTSIDE -> INSIDE
            if prev_state == ZoneState.OUTSIDE and current_state == ZoneState.INSIDE:
                severity = self._determine_severity(track.class_name)
                timestamp_str = datetime.now(timezone.utc).isoformat()

                event = EventPayload(
                    camera_id=cam_id,
                    zone_id=zone_id,
                    track_id=track.track_id,
                    class_name=track.class_name,
                    confidence=track.confidence,
                    bbox=track.bbox,
                    event_type=EventType.INTRUSION.value,
                    severity=severity,
                    timestamp=timestamp_str,
                    evidence_snapshot=encoded_snapshot,
                )
                emitted_events.append(event)

            # Record current state for subsequent frame evaluations
            self._track_states[state_key] = current_state

        return emitted_events

    def cleanup_stale_tracks(self, max_idle_seconds: float = 60.0) -> int:
        """
        Purge tracked state for tracks that have been inactive longer than max_idle_seconds.

        :return: Number of purged state records.
        """
        now = time.time()
        stale_keys = [
            key
            for key, last_time in self._last_seen.items()
            if (now - last_time) > max_idle_seconds
        ]
        for key in stale_keys:
            self._track_states.pop(key, None)
            self._last_seen.pop(key, None)
        return len(stale_keys)

    def reset_zone_states(self, zone_id: str | None = None) -> None:
        """Reset state tracking for a specific zone or all zones."""
        if zone_id is None:
            self._track_states.clear()
            self._last_seen.clear()
        else:
            keys_to_delete = [
                key for key in self._track_states if key[0] == zone_id
            ]
            for key in keys_to_delete:
                self._track_states.pop(key, None)
                self._last_seen.pop(key, None)
