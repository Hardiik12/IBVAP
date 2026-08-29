"""Abstract base class for camera and video ingestion sources."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterator

import numpy as np


class CameraSource(ABC):
    """Abstract base class for all video frame ingestion sources."""

    def __init__(self, camera_id: str, name: str) -> None:
        self.camera_id = camera_id
        self.name = name

    @abstractmethod
    def open(self) -> None:
        """Open video stream or hardware device."""
        ...

    @abstractmethod
    def read_frame(self) -> tuple[bool, np.ndarray | None]:
        """
        Read the next video frame.

        Returns:
            (success: bool, frame: np.ndarray | None) in BGR format.
        """
        ...

    @abstractmethod
    def is_opened(self) -> bool:
        """Check if the video capture device or file is open."""
        ...

    @abstractmethod
    def release(self) -> None:
        """Release underlying video capture hardware/file resources."""
        ...

    @property
    @abstractmethod
    def resolution(self) -> tuple[int, int]:
        """Return (width, height) resolution of the video stream."""
        ...

    @property
    @abstractmethod
    def fps(self) -> float:
        """Return native or target frames-per-second."""
        ...

    def __enter__(self) -> CameraSource:
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.release()

    def __iter__(self) -> Iterator[np.ndarray]:
        """Stream frames as an iterator."""
        if not self.is_opened():
            self.open()
        try:
            while self.is_opened():
                ok, frame = self.read_frame()
                if not ok or frame is None:
                    break
                yield frame
        finally:
            self.release()
