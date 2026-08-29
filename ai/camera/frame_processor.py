import time
import logging
from dataclasses import dataclass
from typing import Tuple, Optional, List
import cv2
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class FrameMetadata:
    """
    Structured metadata representing frame properties.
    """
    frame_id: int
    timestamp: float
    width: int
    height: int
    source_type: str


class FPSCounter:
    """
    Sliding window timer measuring empirical frame processing FPS.
    """

    def __init__(self, window_size: int = 30):
        self.window_size = window_size
        self.timestamps: List[float] = []

    def update(self) -> float:
        """
        Record current timestamp and return average FPS across the sliding window.
        """
        now = time.perf_counter()
        self.timestamps.append(now)
        if len(self.timestamps) > self.window_size:
            self.timestamps.pop(0)

        if len(self.timestamps) < 2:
            return 0.0

        elapsed = self.timestamps[-1] - self.timestamps[0]
        if elapsed <= 0:
            return 0.0

        return (len(self.timestamps) - 1) / elapsed


class FrameProcessor:
    """
    Frame validation, resizing, metadata extraction, and FPS tracking component.
    """

    def __init__(
        self,
        target_width: Optional[int] = None,
        target_height: Optional[int] = None,
        source_type: str = "WEBCAM"
    ):
        self.target_width = target_width
        self.target_height = target_height
        self.source_type = source_type
        self.frame_count = 0
        self.fps_counter = FPSCounter()

    def process(self, frame: np.ndarray) -> Tuple[np.ndarray, FrameMetadata, float]:
        """
        Validates frame integrity, performs optional resizing, extracts metadata,
        and computes moving-average processing FPS.
        """
        if frame is None or not isinstance(frame, np.ndarray):
            raise ValueError("Invalid frame: Frame object is None or not a numpy array")

        if frame.ndim != 3 or frame.shape[0] == 0 or frame.shape[1] == 0:
            raise ValueError(f"Invalid frame dimensions: shape={frame.shape if hasattr(frame, 'shape') else None}")

        self.frame_count += 1
        current_time = time.time()

        processed_frame = frame
        if self.target_width and self.target_height:
            if (processed_frame.shape[1], processed_frame.shape[0]) != (self.target_width, self.target_height):
                processed_frame = cv2.resize(processed_frame, (self.target_width, self.target_height))

        height, width = processed_frame.shape[:2]

        metadata = FrameMetadata(
            frame_id=self.frame_count,
            timestamp=current_time,
            width=width,
            height=height,
            source_type=self.source_type
        )

        current_fps = self.fps_counter.update()
        return processed_frame, metadata, current_fps
