"""
Unified End-to-End AI Analytics Pipeline Orchestrator for IBVAP.

Coordinates:
Camera Ingestion -> Frame Preprocessor -> YOLOv8 Detection -> ByteTrack ->
Virtual Polygon Zone Engine -> Intrusion State Machine -> M1 Event Dispatcher ->
Tactical Visual HUD -> Safe Hardware Resource Cleanup.
"""

from __future__ import annotations

import sys
import argparse
import logging
import time
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple

import cv2
import numpy as np

from ai.core.config import ai_settings
from ai.core.logging import setup_ai_logging
from ai.camera.source import create_camera_source, BaseCameraSource
from ai.camera.frame_processor import FrameProcessor, FrameMetadata
from ai.events.dispatcher import EventDispatcher, DispatchResult

try:
    from ai.events.engine import IntrusionEventEngine
    from ai.events.schemas import EventPayload
    from ai.tracking.schemas import Track
    from ai.tracking.tracker import ByteTracker
    from ai.zones.engine import PolygonZone, ZoneEngine
    from ai.zones.schemas import ZoneConfig, ZoneState
except ImportError:
    IntrusionEventEngine = None  # type: ignore
    EventPayload = None  # type: ignore
    Track = None  # type: ignore
    ByteTracker = None  # type: ignore
    PolygonZone = None  # type: ignore
    ZoneEngine = None  # type: ignore
    ZoneConfig = None  # type: ignore
    ZoneState = None  # type: ignore

logger = logging.getLogger(__name__)


@dataclass
class PipelineResult:
    """Output generated from processing a single video frame through the AI pipeline."""

    frame: np.ndarray
    tracks: list[Any] = field(default_factory=list)
    events: list[Any] = field(default_factory=list)
    fps: float = 0.0
    latency_ms: float = 0.0
    metadata: dict = field(default_factory=dict)


class AIPipeline:
    """
    Core algorithmic pipeline component orchestrating:
    Frame -> ByteTracker (Detection+Tracking) -> ZoneEngine -> IntrusionEventEngine -> Events.
    """

    def __init__(
        self,
        tracker: Optional[Any] = None,
        zone_engine: Optional[Any] = None,
        event_engine: Optional[Any] = None,
        camera_id: str = "cam-01",
    ) -> None:
        self.camera_id = camera_id
        if tracker is not None:
            self.tracker = tracker
        else:
            try:
                self.tracker = ByteTracker() if ByteTracker else None
            except RuntimeError as err:
                if "Ultralytics package is not installed" in str(err):
                    self.tracker = None
                else:
                    raise err



        self.zone_engine = zone_engine or (ZoneEngine() if ZoneEngine else None)
        self.event_engine = event_engine or (IntrusionEventEngine(default_camera_id=camera_id) if IntrusionEventEngine else None)

        self._frame_count = 0
        self._fps_start_time = time.perf_counter()
        self._current_fps = 0.0


    def process_frame(
        self,
        frame: np.ndarray,
        capture_snapshot: bool = True,
    ) -> PipelineResult:
        """
        Process a single BGR video frame through tracking, zone evaluation, and intrusion detection.
        """
        t0 = time.perf_counter()

        tracks = []
        if self.tracker:
            tracks = self.tracker.track(frame)

        triggered_events = []
        if self.zone_engine and self.event_engine:
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
        if self.tracker and hasattr(self.tracker, "reset"):
            self.tracker.reset()
        if self.event_engine and hasattr(self.event_engine, "reset_zone_states"):
            self.event_engine.reset_zone_states()


class CameraPipelineRunner:
    """
    Main Computer Vision Camera & Live Inference Pipeline Runner.
    Unifies Camera Ingestion, Frame Validation, YOLO/ByteTrack, Zone Containment,
    Live M1 Event Dispatching, Tactical Diagnostic HUD, and Safe Resource Cleanup.
    """

    def __init__(
        self,
        source_type: Optional[str] = None,
        camera_index: Optional[int] = None,
        video_path: Optional[str] = None,
        target_width: Optional[int] = None,
        target_height: Optional[int] = None,
        display_preview: Optional[bool] = None,
        enable_ai: bool = True,
        camera_id: Optional[str] = None,
        zone_id: Optional[str] = None,
        tracker: Optional[Any] = None,
        zone_engine: Optional[Any] = None,
        event_engine: Optional[Any] = None,
        dispatcher: Optional[EventDispatcher] = None,
        dispatch_to_backend: bool = True,
    ):
        self.source_type = (source_type or ai_settings.SOURCE_TYPE).upper()
        self.camera_index = camera_index if camera_index is not None else ai_settings.CAMERA_INDEX
        self.video_path = video_path or ai_settings.VIDEO_PATH
        self.target_width = target_width or ai_settings.FRAME_WIDTH
        self.target_height = target_height or ai_settings.FRAME_HEIGHT
        self.display_preview = display_preview if display_preview is not None else ai_settings.DISPLAY_PREVIEW

        self.enable_ai = enable_ai and (ByteTracker is not None)
        self.camera_id = camera_id or ai_settings.CAMERA_ID or "cam-webcam-01"
        self.zone_id = zone_id or ai_settings.ZONE_ID
        self.dispatch_to_backend = dispatch_to_backend

        # Camera & Preprocessor
        self.source: BaseCameraSource = create_camera_source(
            source_type=self.source_type,
            camera_index=self.camera_index,
            video_path=self.video_path,
        )
        self.processor = FrameProcessor(
            target_width=self.target_width,
            target_height=self.target_height,
            source_type=self.source_type,
        )

        # AI Engine & Dispatcher
        if self.enable_ai:
            self.ai_pipeline = AIPipeline(
                tracker=tracker,
                zone_engine=zone_engine,
                event_engine=event_engine,
                camera_id=self.camera_id,
            )
        else:
            self.ai_pipeline = None

        self.dispatcher = dispatcher or EventDispatcher()

        # UI Overlay state
        self._recent_intrusions: List[Dict[str, Any]] = []
        self._total_dispatched_events = 0

    def validate_backend_connection(self) -> bool:
        """Pre-flight check: Validates camera and zone on M1 backend if configured."""
        if not self.dispatch_to_backend:
            return True

        if not self.camera_id or len(self.camera_id) != 36:
            logger.info(f"Using local camera identifier '{self.camera_id}' (bypassing pre-flight UUID check).")
            return True

        valid, cam_data, zone_data = self.dispatcher.validate_camera_and_zone(
            camera_id=self.camera_id,
            zone_id=self.zone_id,
        )

        # If zone polygon coordinates returned by backend, dynamically configure ZoneEngine
        if valid and zone_data and self.ai_pipeline and self.ai_pipeline.zone_engine and PolygonZone and ZoneConfig:
            poly_coords = zone_data.get("polygon_coordinates")
            if poly_coords:
                config = ZoneConfig(
                    zone_id=zone_data.get("id", self.zone_id or "zone-01"),
                    name=zone_data.get("name", "Backend Restricted Zone"),
                    polygon_coordinates=poly_coords,
                    is_normalized=True,
                    camera_id=self.camera_id,
                )
                backend_zone = PolygonZone(config)
                self.ai_pipeline.zone_engine.add_zone(backend_zone)
                logger.info(f"Loaded zone polygon from backend: '{config.name}' ({len(poly_coords)} vertices).")

        return valid

    def draw_diagnostic_overlay(
        self,
        frame: np.ndarray,
        current_fps: float,
        width: int,
        height: int,
    ) -> np.ndarray:
        """Backward-compatible helper delegating to draw_tactical_hud."""
        return self.draw_tactical_hud(
            frame=frame,
            current_fps=current_fps,
            width=width,
            height=height,
            tracks=[],
            events=[],
        )

    def draw_tactical_hud(

        self,
        frame: np.ndarray,
        current_fps: float,
        width: int,
        height: int,
        tracks: List[Any],
        events: List[Any],
    ) -> np.ndarray:
        """
        Draws comprehensive tactical security overlay (Bounding boxes, Track IDs,
        Polygon Zones, Foot Points, Intrusion Alert Banners, and Telemetry Header).
        """
        annotated = frame.copy()
        now = time.time()

        # 1. Draw Virtual Polygon Zones
        if self.ai_pipeline and self.ai_pipeline.zone_engine:
            for zone in self.ai_pipeline.zone_engine.zones:
                if hasattr(zone, "set_frame_resolution") and zone.config.is_normalized:
                    zone.set_frame_resolution(width, height)

                pts = zone._polygon_np.astype(np.int32).reshape((-1, 1, 2))
                
                # Check if zone is currently occupied
                is_occupied = any(
                    getattr(t, "current_zone_state", "OUTSIDE") == "INSIDE" for t in tracks
                )
                zone_color = (0, 0, 255) if is_occupied else (0, 255, 0)
                
                # Semi-transparent filled polygon
                overlay_poly = annotated.copy()
                cv2.fillPoly(overlay_poly, [pts], zone_color)
                cv2.addWeighted(overlay_poly, 0.15, annotated, 0.85, 0, annotated)
                
                # Solid border
                cv2.polylines(annotated, [pts], isClosed=True, color=zone_color, thickness=2)
                
                # Zone label
                centroid_x = int(np.mean(pts[:, 0, 0]))
                centroid_y = int(np.mean(pts[:, 0, 1]))
                cv2.putText(
                    annotated,
                    f"ZONE: {zone.config.name}",
                    (centroid_x - 50, centroid_y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    zone_color,
                    1,
                    cv2.LINE_AA,
                )

        # 2. Draw Active Tracks & Foot Reference Points
        for t in tracks:
            bbox = getattr(t, "bbox", None)
            if not bbox or len(bbox) != 4:
                continue

            x1, y1, x2, y2 = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
            track_id = getattr(t, "track_id", -1)
            class_name = getattr(t, "class_name", "object")
            conf = getattr(t, "confidence", 0.0)
            state = getattr(t, "current_zone_state", "OUTSIDE")

            box_color = (0, 0, 255) if state == "INSIDE" else (0, 255, 0)

            # Bounding Box
            cv2.rectangle(annotated, (x1, y1), (x2, y2), box_color, 2)

            # Foot Reference Point
            ref_pt = getattr(t, "reference_point", ((x1 + x2) // 2, y2))
            rx, ry = int(ref_pt[0]), int(ref_pt[1])
            cv2.circle(annotated, (rx, ry), 5, (0, 255, 255), -1)

            # Track Label Tag
            label = f"ID:{track_id} {class_name} {conf:.2f} [{state}]"
            cv2.rectangle(annotated, (x1, max(0, y1 - 20)), (x1 + len(label) * 8 + 10, y1), box_color, -1)
            cv2.putText(
                annotated,
                label,
                (x1 + 4, max(14, y1 - 5)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                (0, 0, 0),
                1,
                cv2.LINE_AA,
            )

        # 3. Process & Maintain Recent Intrusion Alerts
        for evt in events:
            self._recent_intrusions.append(
                {
                    "track_id": getattr(evt, "track_id", 0),
                    "class_name": getattr(evt, "class_name", "person"),
                    "zone_id": getattr(evt, "zone_id", "Zone"),
                    "timestamp": now,
                }
            )

        # Retain intrusions for 3 seconds for visual alerting
        self._recent_intrusions = [
            item for item in self._recent_intrusions if now - item["timestamp"] < 3.0
        ]

        # 4. Draw Intrusion Alert Banner if active
        if self._recent_intrusions:
            latest = self._recent_intrusions[-1]
            banner_text = f"🚨 INTRUSION ALERT: Track #{latest['track_id']} ({latest['class_name']}) in {latest['zone_id']}"
            cv2.rectangle(annotated, (10, height - 55), (width - 10, height - 15), (0, 0, 200), -1)
            cv2.rectangle(annotated, (10, height - 55), (width - 10, height - 15), (255, 255, 255), 2)
            cv2.putText(
                annotated,
                banner_text,
                (25, height - 26),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

        # 5. Diagnostic Header HUD
        cv2.rectangle(annotated, (10, 10), (380, 115), (0, 0, 0), -1)
        cv2.rectangle(annotated, (10, 10), (380, 115), (0, 255, 0), 1)

        fps_text = f"FPS: {current_fps:.1f}"
        res_text = f"Resolution: {width}x{height} | Src: {self.source_type}"
        track_text = f"Active Tracks: {len(tracks)} | Frame: {self.processor.frame_count}"
        dispatch_text = f"Dispatched Events: {self._total_dispatched_events}"

        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = 0.45
        color = (0, 255, 0)

        cv2.putText(annotated, fps_text, (20, 32), font, scale, color, 1, cv2.LINE_AA)
        cv2.putText(annotated, res_text, (20, 52), font, scale, color, 1, cv2.LINE_AA)
        cv2.putText(annotated, track_text, (20, 72), font, scale, color, 1, cv2.LINE_AA)
        cv2.putText(annotated, dispatch_text, (20, 92), font, scale, (0, 255, 255), 1, cv2.LINE_AA)

        return annotated

    def run(self, max_frames: Optional[int] = None) -> int:
        """
        Executes the unified live processing loop:
        Capture -> Validate -> YOLO/ByteTrack -> Zone Containment -> M1 Event Dispatch -> HUD -> Cleanup.
        """
        logger.info(
            f"Starting IBVAP Unified AI Pipeline (Source={self.source_type}, AI={self.enable_ai}, Dispatch={self.dispatch_to_backend})..."
        )

        try:
            self.validate_backend_connection()
            self.source.open()

            while True:
                success, frame = self.source.read()
                if not success or frame is None:
                    logger.info("End of video stream or camera ingestion stopped.")
                    break

                # Frame preprocessing & FPS measurement
                processed_frame, metadata, current_fps = self.processor.process(frame)

                tracks: List[Any] = []
                events: List[Any] = []

                # AI Inference & Spatial Logic
                if self.ai_pipeline:
                    pipeline_res = self.ai_pipeline.process_frame(processed_frame, capture_snapshot=True)
                    tracks = pipeline_res.tracks
                    events = pipeline_res.events

                    # Dispatch newly emitted intrusion events to M1 backend
                    if events and self.dispatch_to_backend and self.dispatcher:
                        for evt in events:
                            target_zone = getattr(evt, "zone_id", self.zone_id)
                            res = self.dispatcher.dispatch_event(
                                payload=evt,
                                camera_id=self.camera_id,
                                zone_id=target_zone,
                            )
                            if res.success:
                                self._total_dispatched_events += 1

                # Live HUD Rendering & Display
                if self.display_preview:
                    overlay_frame = self.draw_tactical_hud(
                        frame=processed_frame,
                        current_fps=current_fps,
                        width=metadata.width,
                        height=metadata.height,
                        tracks=tracks,
                        events=events,
                    )
                    window_title = f"IBVAP Tactical HUD — Live AI Pipeline ({self.source_type})"
                    cv2.imshow(window_title, overlay_frame)

                    key = cv2.waitKey(1) & 0xFF
                    if key == ord("q") or key == 27:  # 'q' or ESC
                        logger.info("User requested shutdown via keyboard input ('q' or 'ESC').")
                        break

                if max_frames and self.processor.frame_count >= max_frames:
                    logger.info(f"Reached configured max_frames limit ({max_frames}).")
                    break

        except Exception as e:
            logger.error(f"Error during unified AI pipeline execution: {e}")
            raise e
        finally:
            self.source.release()
            if self.display_preview:
                try:
                    cv2.destroyAllWindows()
                except Exception:
                    pass
            logger.info(
                f"Unified AI Pipeline stopped cleanly. Total processed frames: {self.processor.frame_count}, Dispatched events: {self._total_dispatched_events}"
            )

        return self.processor.frame_count


def main():
    setup_ai_logging()
    parser = argparse.ArgumentParser(description="IBVAP Unified Live AI Analytics Pipeline")
    parser.add_argument("--source", choices=["webcam", "video_file"], default="webcam", help="Input source type")
    parser.add_argument("--index", type=int, default=0, help="Webcam device index")
    parser.add_argument("--path", type=str, default=None, help="Video file path for video_file mode")
    parser.add_argument("--width", type=int, default=None, help="Target frame width")
    parser.add_argument("--height", type=int, default=None, help="Target frame height")
    parser.add_argument("--camera-id", type=str, default=None, help="M1 Backend Camera UUID")
    parser.add_argument("--zone-id", type=str, default=None, help="M1 Backend Zone UUID")
    parser.add_argument("--headless", action="store_true", help="Disable live preview GUI window")
    parser.add_argument("--no-ai", action="store_true", help="Disable AI inference (ingestion-only mode)")
    parser.add_argument("--no-dispatch", action="store_true", help="Disable M1 backend event dispatching")
    parser.add_argument("--max-frames", type=int, default=None, help="Stop after N frames")

    args = parser.parse_args()

    runner = CameraPipelineRunner(
        source_type=args.source.upper(),
        camera_index=args.index,
        video_path=args.path,
        target_width=args.width,
        target_height=args.height,
        display_preview=not args.headless,
        enable_ai=not args.no_ai,
        camera_id=args.camera_id,
        zone_id=args.zone_id,
        dispatch_to_backend=not args.no_dispatch,
    )
    runner.run(max_frames=args.max_frames)


if __name__ == "__main__":
    main()
