"""Recorded video file ingestion source (offline/fallback testing)."""

from __future__ import annotations

import os

import cv2
import numpy as np

from ai.camera.base import CameraSource


class VideoFileSource(CameraSource):
    """Ingests frames from a recorded video file (e.g. mp4, avi)."""

    def __init__(
        self,
        file_path: str,
        camera_id: str = "file-cam-01",
        name: str = "Video File Source",
        loop: bool = False,
    ) -> None:
        super().__init__(camera_id=camera_id, name=name)
        self.file_path = file_path
        self.loop = loop
        self._cap: cv2.VideoCapture | None = None

    def open(self) -> None:
        """Open the video file for reading."""
        if self._cap is not None and self._cap.isOpened():
            return

        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Video file not found at path: {self.file_path}")

        self._cap = cv2.VideoCapture(self.file_path)
        if not self._cap.isOpened():
            raise RuntimeError(f"Could not open video file: {self.file_path}")

    def read_frame(self) -> tuple[bool, np.ndarray | None]:
        """Read the next video frame, automatically looping if configured."""
        if self._cap is None or not self._cap.isOpened():
            self.open()

        assert self._cap is not None
        ok, frame = self._cap.read()

        if not ok or frame is None:
            if self.loop:
                # Rewind to start
                self._cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ok, frame = self._cap.read()
                if not ok or frame is None:
                    return False, None
                return True, frame
            return False, None

        return True, frame

    def is_opened(self) -> bool:
        """Check if video file capture is open."""
        return self._cap is not None and self._cap.isOpened()

    def release(self) -> None:
        """Close video file stream."""
        if self._cap is not None:
            self._cap.release()
            self._cap = None

    @property
    def total_frames(self) -> int:
        """Total frame count in video file."""
        if self._cap is not None and self._cap.isOpened():
            return int(self._cap.get(cv2.CAP_PROP_FRAME_COUNT))
        return 0

    @property
    def resolution(self) -> tuple[int, int]:
        """Return (width, height) of the video file."""
        if self._cap is not None and self._cap.isOpened():
            return (
                int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            )
        return (640, 480)

    @property
    def fps(self) -> float:
        """Return frame rate of the video file."""
        if self._cap is not None and self._cap.isOpened():
            val = self._cap.get(cv2.CAP_PROP_FPS)
            if val > 0:
                return float(val)
        return 30.0
