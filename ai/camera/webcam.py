"""Webcam video ingestion source (USB / Built-in camera)."""

from __future__ import annotations

import cv2
import numpy as np

from ai.camera.base import CameraSource


class WebcamSource(CameraSource):
    """Ingests frames from a local USB or built-in webcam via OpenCV."""

    def __init__(
        self,
        camera_id: str = "cam-01",
        name: str = "Local Webcam",
        camera_index: int = 0,
        target_width: int | None = None,
        target_height: int | None = None,
        target_fps: int | None = None,
    ) -> None:
        super().__init__(camera_id=camera_id, name=name)
        self.camera_index = camera_index
        self.target_width = target_width
        self.target_height = target_height
        self.target_fps = target_fps
        self._cap: cv2.VideoCapture | None = None

    def open(self) -> None:
        """Open the webcam device."""
        if self._cap is not None and self._cap.isOpened():
            return

        self._cap = cv2.VideoCapture(self.camera_index)
        if not self._cap.isOpened():
            raise RuntimeError(
                f"Failed to open webcam index {self.camera_index}. "
                "Verify camera connection and permissions."
            )

        if self.target_width is not None:
            self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.target_width)
        if self.target_height is not None:
            self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.target_height)
        if self.target_fps is not None:
            self._cap.set(cv2.CAP_PROP_FPS, self.target_fps)

    def read_frame(self) -> tuple[bool, np.ndarray | None]:
        """Read a single frame from the webcam."""
        if self._cap is None or not self._cap.isOpened():
            self.open()

        assert self._cap is not None
        ok, frame = self._cap.read()
        if not ok or frame is None:
            return False, None
        return True, frame

    def is_opened(self) -> bool:
        """Check if webcam capture is active."""
        return self._cap is not None and self._cap.isOpened()

    def release(self) -> None:
        """Release webcam resources."""
        if self._cap is not None:
            self._cap.release()
            self._cap = None

    @property
    def resolution(self) -> tuple[int, int]:
        """Return current (width, height) of the webcam stream."""
        if self._cap is not None and self._cap.isOpened():
            width = int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            return (width, height)
        return (self.target_width or 640, self.target_height or 480)

    @property
    def fps(self) -> float:
        """Return native or configured frame rate."""
        if self._cap is not None and self._cap.isOpened():
            val = self._cap.get(cv2.CAP_PROP_FPS)
            if val > 0:
                return float(val)
        return float(self.target_fps or 30.0)
