import os
import logging
from abc import ABC, abstractmethod
from typing import Tuple, Optional, Any
import cv2
import numpy as np

logger = logging.getLogger(__name__)


class BaseCameraSource(ABC):
    """
    Abstract Base Class for video/camera sources.
    """

    @abstractmethod
    def open(self) -> bool:
        """Open the camera device or video stream."""
        pass

    @abstractmethod
    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Read the next video frame.
        Returns (success: bool, frame: Optional[np.ndarray]).
        """
        pass

    @abstractmethod
    def release(self) -> None:
        """Release device hardware or file handle resources."""
        pass

    @abstractmethod
    def is_opened(self) -> bool:
        """Check if source stream is actively open."""
        pass

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()


class WebcamSource(BaseCameraSource):
    """
    Camera source implementation for local/USB webcams via OpenCV.
    """

    def __init__(self, camera_index: int = 0):
        self.camera_index = camera_index
        self.cap: Optional[cv2.VideoCapture] = None

    def open(self) -> bool:
        logger.info(f"Opening webcam index {self.camera_index}...")
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            logger.error(f"Failed to open webcam at index {self.camera_index}.")
            raise RuntimeError(f"Failed to open webcam at device index {self.camera_index}")
        logger.info(f"Webcam index {self.camera_index} opened successfully.")
        return True

    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        if not self.cap or not self.cap.isOpened():
            return False, None
        success, frame = self.cap.read()
        if not success or frame is None:
            return False, None
        return True, frame

    def release(self) -> None:
        if self.cap and self.cap.isOpened():
            self.cap.release()
            logger.info(f"Webcam index {self.camera_index} released.")
        self.cap = None

    def is_opened(self) -> bool:
        return self.cap is not None and self.cap.isOpened()


class VideoFileSource(BaseCameraSource):
    """
    Camera source implementation for local video files (fallback source).
    """

    def __init__(self, video_path: str):
        if not video_path:
            raise ValueError("Video file path must be specified for VIDEO_FILE mode")
        self.video_path = video_path
        self.cap: Optional[cv2.VideoCapture] = None

    def open(self) -> bool:
        if not os.path.exists(self.video_path):
            logger.error(f"Video file not found at path: '{self.video_path}'")
            raise FileNotFoundError(f"Video file not found: '{self.video_path}'")

        logger.info(f"Opening video file source: '{self.video_path}'...")
        self.cap = cv2.VideoCapture(self.video_path)
        if not self.cap.isOpened():
            logger.error(f"OpenCV failed to open video file at path: '{self.video_path}'")
            raise RuntimeError(f"Failed to open video file at path: '{self.video_path}'")

        logger.info(f"Video file source '{self.video_path}' opened successfully.")
        return True

    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        if not self.cap or not self.cap.isOpened():
            return False, None
        success, frame = self.cap.read()
        if not success or frame is None:
            logger.info("Video file stream reached End-Of-File (EOF).")
            return False, None
        return True, frame

    def release(self) -> None:
        if self.cap and self.cap.isOpened():
            self.cap.release()
            logger.info(f"Video file source '{self.video_path}' released.")
        self.cap = None

    def is_opened(self) -> bool:
        return self.cap is not None and self.cap.isOpened()


def create_camera_source(
    source_type: str,
    camera_index: int = 0,
    video_path: Optional[str] = None,
    rtsp_url: Optional[str] = None,
    camera_id: str = "cam-01",
    name: Optional[str] = None,
    **kwargs: Any,
) -> BaseCameraSource:
    """
    Factory function instantiating the requested camera source implementation.
    Supports: WEBCAM, VIDEO_FILE, RTSP, SYNTHETIC.
    """
    source_str = source_type.strip().upper()
    if source_str == "WEBCAM":
        return WebcamSource(camera_index=camera_index)
    elif source_str == "VIDEO_FILE":
        if not video_path:
            raise ValueError("VIDEO_PATH configuration is required when SOURCE_TYPE is VIDEO_FILE")
        return VideoFileSource(video_path=video_path)
    elif source_str == "RTSP":
        if not rtsp_url:
            raise ValueError("RTSP_URL configuration is required when SOURCE_TYPE is RTSP")
        from ai.camera.rtsp import RTSPCameraSource
        return RTSPCameraSource(
            rtsp_url=rtsp_url,
            camera_id=camera_id,
            name=name or "RTSP Camera Source",
            **kwargs,
        )
    elif source_str == "SYNTHETIC":
        from ai.camera.synthetic import SyntheticSource
        return SyntheticSource(
            camera_id=camera_id,
            name=name or "Synthetic Stream",
            **kwargs,
        )
    else:
        raise ValueError(
            f"Unsupported SOURCE_TYPE: '{source_type}'. "
            "Supported options: WEBCAM, VIDEO_FILE, RTSP, SYNTHETIC"
        )
