"""End-to-end AI analytics pipeline orchestrator for IBVAP."""

from __future__ import annotations

import sys
import argparse
import logging
import time
from dataclasses import dataclass, field
from typing import Optional

import cv2
import numpy as np

from ai.core.config import ai_settings
from ai.core.logging import setup_ai_logging
from ai.camera.source import create_camera_source, BaseCameraSource
from ai.camera.frame_processor import FrameProcessor
from ai.events.engine import IntrusionEventEngine
from ai.events.schemas import EventPayload
from ai.tracking.schemas import Track
from ai.tracking.tracker import ByteTracker
from ai.zones.engine import ZoneEngine

logger = logging.getLogger(__name__)


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


class CameraPipelineRunner:
    """
    Main Computer Vision Camera & Frame Processing Pipeline Runner.
    Coordinates camera ingestion, frame processing, FPS calculation, overlay graphics,
    headless execution, and safe resource cleanup.
    """

    def __init__(
        self,
        source_type: Optional[str] = None,
        camera_index: Optional[int] = None,
        video_path: Optional[str] = None,
        target_width: Optional[int] = None,
        target_height: Optional[int] = None,
        display_preview: Optional[bool] = None
    ):
        self.source_type = (source_type or ai_settings.SOURCE_TYPE).upper()
        self.camera_index = camera_index if camera_index is not None else ai_settings.CAMERA_INDEX
        self.video_path = video_path or ai_settings.VIDEO_PATH
        self.target_width = target_width or ai_settings.FRAME_WIDTH
        self.target_height = target_height or ai_settings.FRAME_HEIGHT
        self.display_preview = display_preview if display_preview is not None else ai_settings.DISPLAY_PREVIEW

        self.source: BaseCameraSource = create_camera_source(
            source_type=self.source_type,
            camera_index=self.camera_index,
            video_path=self.video_path
        )
        self.processor = FrameProcessor(
            target_width=self.target_width,
            target_height=self.target_height,
            source_type=self.source_type
        )

    def draw_diagnostic_overlay(self, frame: np.ndarray, current_fps: float, width: int, height: int) -> np.ndarray:
        """
        Draws diagnostic telemetry overlay on live frame (FPS, Resolution, Source, Frame ID).
        """
        annotated = frame.copy()
        
        # Dark semi-transparent banner for readability
        cv2.rectangle(annotated, (10, 10), (320, 110), (0, 0, 0), -1)
        cv2.rectangle(annotated, (10, 10), (320, 110), (0, 255, 0), 1)

        fps_text = f"FPS: {current_fps:.1f}"
        res_text = f"Resolution: {width}x{height}"
        src_text = f"Source: {self.source_type}"
        frame_text = f"Frame #: {self.processor.frame_count}"

        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = 0.5
        color = (0, 255, 0)
        thickness = 1

        cv2.putText(annotated, fps_text, (20, 32), font, scale, color, thickness, cv2.LINE_AA)
        cv2.putText(annotated, res_text, (20, 52), font, scale, color, thickness, cv2.LINE_AA)
        cv2.putText(annotated, src_text, (20, 72), font, scale, color, thickness, cv2.LINE_AA)
        cv2.putText(annotated, frame_text, (20, 92), font, scale, color, thickness, cv2.LINE_AA)

        return annotated

    def run(self, max_frames: Optional[int] = None) -> int:
        """
        Executes the frame processing loop until EOF, max_frames, or user exit signal ('q'/'ESC').
        Returns total number of processed frames.
        """
        logger.info(f"Starting M2.1 AI Camera Pipeline (Source={self.source_type}, Preview={self.display_preview})...")
        
        try:
            self.source.open()
            
            while True:
                success, frame = self.source.read()
                if not success or frame is None:
                    logger.info("End of stream or frame capture stopped.")
                    break

                processed_frame, metadata, current_fps = self.processor.process(frame)

                if self.display_preview:
                    overlay_frame = self.draw_diagnostic_overlay(
                        processed_frame,
                        current_fps=current_fps,
                        width=metadata.width,
                        height=metadata.height
                    )
                    window_title = f"IBVAP AI Pipeline — M2.1 Preview ({self.source_type})"
                    cv2.imshow(window_title, overlay_frame)

                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q') or key == 27:  # 'q' or ESC
                        logger.info("User requested shutdown via keyboard input ('q' or 'ESC').")
                        break

                if max_frames and self.processor.frame_count >= max_frames:
                    logger.info(f"Reached configured max_frames limit ({max_frames}).")
                    break

        except Exception as e:
            logger.error(f"Error during AI camera pipeline execution: {e}")
            raise e
        finally:
            self.source.release()
            if self.display_preview:
                try:
                    cv2.destroyAllWindows()
                except Exception:
                    pass
            logger.info(f"AI camera pipeline stopped cleanly. Total processed frames: {self.processor.frame_count}")

        return self.processor.frame_count


def main():
    setup_ai_logging()
    parser = argparse.ArgumentParser(description="IBVAP M2.1 AI Camera & Frame Processing Pipeline")
    parser.add_argument("--source", choices=["webcam", "video_file"], default="webcam", help="Input source type")
    parser.add_argument("--index", type=int, default=0, help="Webcam device index")
    parser.add_argument("--path", type=str, default=None, help="Video file path for video_file mode")
    parser.add_argument("--width", type=int, default=None, help="Target frame width")
    parser.add_argument("--height", type=int, default=None, help="Target frame height")
    parser.add_argument("--headless", action="store_true", help="Disable live preview GUI window")
    parser.add_argument("--max-frames", type=int, default=None, help="Stop after N frames")

    args = parser.parse_args()

    runner = CameraPipelineRunner(
        source_type=args.source.upper(),
        camera_index=args.index,
        video_path=args.path,
        target_width=args.width,
        target_height=args.height,
        display_preview=not args.headless
    )
    runner.run(max_frames=args.max_frames)


if __name__ == "__main__":
    main()
