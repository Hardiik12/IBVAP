"""Synthetic camera generator for automated testing and CI pipelines."""

from __future__ import annotations

import numpy as np

from ai.camera.base import CameraSource


class SyntheticSource(CameraSource):
    """Generates synthetic RGB frames (useful for CI and headless testing)."""

    def __init__(
        self,
        camera_id: str = "synthetic-01",
        name: str = "Synthetic Stream",
        width: int = 640,
        height: int = 480,
        fps: float = 30.0,
        max_frames: int | None = None,
    ) -> None:
        super().__init__(camera_id=camera_id, name=name)
        self._width = width
        self._height = height
        self._fps = fps
        self._max_frames = max_frames
        self._current_frame = 0
        self._opened = False

    def open(self) -> None:
        self._opened = True
        self._current_frame = 0

    def read_frame(self) -> tuple[bool, np.ndarray | None]:
        if not self._opened:
            self.open()

        if self._max_frames is not None and self._current_frame >= self._max_frames:
            return False, None

        # Create a simple frame with changing color intensity
        color_val = (self._current_frame * 10) % 255
        frame = np.full((self._height, self._width, 3), fill_value=color_val, dtype=np.uint8)
        self._current_frame += 1
        return True, frame

    def is_opened(self) -> bool:
        return self._opened

    def release(self) -> None:
        self._opened = False

    @property
    def resolution(self) -> tuple[int, int]:
        return (self._width, self._height)

    @property
    def fps(self) -> float:
        return self._fps
