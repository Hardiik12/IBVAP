"""Production-grade RTSP IP camera ingestion source with non-blocking grabber and auto-reconnect."""

from __future__ import annotations

import logging
import os
import random
import re
import threading
import time
from enum import Enum
from typing import Any, Optional, Tuple

import cv2
import numpy as np

from ai.camera.base import CameraSource
from ai.camera.source import BaseCameraSource

logger = logging.getLogger(__name__)


def sanitize_rtsp_url(url: Optional[str]) -> str:
    """
    Sanitizes RTSP stream URLs by masking plaintext credentials.
    
    Example:
        'rtsp://admin:SecretPass123@192.168.1.100:554/h264'
        -> 'rtsp://admin:***@192.168.1.100:554/h264'
    """
    if not url:
        return ""
    # Redact password embedded in protocol://username:password@host
    return re.sub(r"://([^:]+):([^@]+)@", r"://:***@", str(url))


class CameraState(str, Enum):
    """Lifecycle states for RTSP stream connection."""

    DISCONNECTED = "DISCONNECTED"
    CONNECTING = "CONNECTING"
    STREAMING = "STREAMING"
    STALE = "STALE"
    RECONNECTING = "RECONNECTING"
    ERROR = "ERROR"
    STOPPED = "STOPPED"


class RTSPCameraSource(CameraSource, BaseCameraSource):
    """
    Resilient, non-blocking RTSP stream ingestion source.
    
    Key Engineering Principles:
    1. Zero Inference Blocking: Frame grabbing executes in a dedicated background worker thread.
    2. Latest Frame Priority: Overwrites a single atomic slot; unconsumed old frames are dropped.
    3. Stale Frame Watchdog: Detects stream freezes and transitions state to STALE/RECONNECTING.
    4. Bounded Exponential Backoff: Automatically reconnects on network dropouts with jitter.
    5. Credential Sanitization: Raw passwords never leak into logs, exceptions, or status dictionaries.
    """

    def __init__(
        self,
        rtsp_url: str,
        camera_id: str = "rtsp-cam-01",
        name: str = "RTSP Camera Source",
        reconnect_interval_base: float = 1.0,
        reconnect_interval_max: float = 30.0,
        stale_frame_timeout: float = 3.0,
        tcp_transport: bool = True,
        socket_timeout_us: int = 5000000,
        target_width: Optional[int] = None,
        target_height: Optional[int] = None,
        target_fps: Optional[float] = None,
    ) -> None:
        if not rtsp_url or not isinstance(rtsp_url, str):
            raise ValueError("RTSP URL must be a non-empty string.")

        sanitized = sanitize_rtsp_url(rtsp_url)
        if not (rtsp_url.startswith("rtsp://") or rtsp_url.startswith("rtsps://")):
            raise ValueError(f"Invalid RTSP URL scheme. Expected 'rtsp://' or 'rtsps://', got: '{sanitized}'")

        super().__init__(camera_id=camera_id, name=name)

        self.rtsp_url = rtsp_url
        self._sanitized_url = sanitized
        self.reconnect_interval_base = max(0.1, float(reconnect_interval_base))
        self.reconnect_interval_max = max(self.reconnect_interval_base, float(reconnect_interval_max))
        self.stale_frame_timeout = max(0.5, float(stale_frame_timeout))
        self.tcp_transport = tcp_transport
        self.socket_timeout_us = socket_timeout_us

        self.target_width = target_width
        self.target_height = target_height
        self.target_fps = target_fps

        # Threading & Synchronization
        self._cap: Optional[cv2.VideoCapture] = None
        self._worker_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()

        # Frame Buffer (Single-Slot Atomic Latest Frame)
        self._latest_frame: Optional[np.ndarray] = None
        self._last_frame_timestamp: float = 0.0

        # Observability & Metrics
        self._state: CameraState = CameraState.DISCONNECTED
        self._reconnect_count: int = 0
        self._dropped_frames: int = 0
        self._total_frames_received: int = 0
        self._consecutive_failures: int = 0
        self._native_width: int = target_width or 640
        self._native_height: int = target_height or 480
        self._native_fps: float = target_fps or 30.0

    @property
    def state(self) -> CameraState:
        """Return current connection lifecycle state."""
        return self._state

    @property
    def sanitized_url(self) -> str:
        """Return URL with redacted credentials."""
        return self._sanitized_url

    def open(self) -> bool:
        """
        Starts the background RTSP acquisition thread.
        Returns True if thread started successfully.
        """
        with self._lock:
            if self._worker_thread is not None and self._worker_thread.is_alive():
                return True

            self._stop_event.clear()
            self._state = CameraState.CONNECTING
            logger.info(f"Opening RTSP camera stream [{self.camera_id}]: {self._sanitized_url}")

            self._worker_thread = threading.Thread(
                target=self._capture_loop,
                name=f"RTSPGrabber-{self.camera_id}",
                daemon=True,
            )
            self._worker_thread.start()
            return True

    def _apply_capture_options(self) -> None:
        """Configures FFmpeg transport and socket options via environment / properties."""
        options = []
        if self.tcp_transport:
            options.append("rtsp_transport;tcp")
        if self.socket_timeout_us > 0:
            options.append(f"stimeout;{self.socket_timeout_us}")
        options.append("buffer_size;1024000")

        os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "|".join(options)

    def _open_capture(self) -> bool:
        """Internal helper to instantiate and open cv2.VideoCapture with options."""
        self._apply_capture_options()
        try:
            cap = cv2.VideoCapture(self.rtsp_url, cv2.CAP_FFMPEG)
            if not cap.isOpened():
                # Fallback to default backend if CAP_FFMPEG flag fails
                cap = cv2.VideoCapture(self.rtsp_url)

            if cap.isOpened():
                # Configure minimal buffer to prevent internal queuing
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                
                # Query stream properties
                w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                f = float(cap.get(cv2.CAP_PROP_FPS))
                if w > 0 and h > 0:
                    self._native_width = w
                    self._native_height = h
                if f > 0:
                    self._native_fps = f

                self._cap = cap
                return True
            else:
                cap.release()
                return False
        except Exception as e:
            logger.warning(f"Exception opening RTSP stream [{self.camera_id}] ({self._sanitized_url}): {e}")
            return False

    def _capture_loop(self) -> None:
        """
        Dedicated background thread continuously pulling frames, handling
        reconnection backoff, and updating the single-slot latest-frame buffer.
        """
        attempt = 0

        while not self._stop_event.is_set():
            if self._cap is None or not self._cap.isOpened():
                self._state = CameraState.CONNECTING if attempt == 0 else CameraState.RECONNECTING
                success = self._open_capture()

                if not success:
                    attempt += 1
                    self._consecutive_failures += 1
                    self._reconnect_count += 1
                    
                    # Bounded exponential backoff with random jitter
                    delay = min(
                        self.reconnect_interval_max,
                        self.reconnect_interval_base * (2 ** min(attempt, 6))
                    )
                    jitter = random.uniform(-0.25 * delay, 0.25 * delay)
                    total_delay = max(0.2, delay + jitter)

                    logger.warning(
                        f"RTSP stream [{self.camera_id}] connection failed (attempt {attempt}). "
                        f"Retrying in {total_delay:.2f}s..."
                    )
                    self._state = CameraState.RECONNECTING
                    
                    # Sleep in small slices to remain responsive to shutdown signal
                    slept = 0.0
                    while slept < total_delay and not self._stop_event.is_set():
                        time.sleep(0.1)
                        slept += 0.1
                    continue

                # Successfully connected
                attempt = 0
                self._consecutive_failures = 0
                self._state = CameraState.STREAMING
                logger.info(
                    f"RTSP stream [{self.camera_id}] connected successfully. "
                    f"Resolution: {self._native_width}x{self._native_height} @ {self._native_fps:.1f} FPS"
                )

            # Read frame from stream
            try:
                ok, frame = self._cap.read()
                if not ok or frame is None:
                    logger.warning(f"RTSP stream [{self.camera_id}] frame read returned empty/error. Triggering reconnect.")
                    self._state = CameraState.RECONNECTING
                    if self._cap is not None:
                        self._cap.release()
                        self._cap = None
                    continue

                now = time.time()
                with self._lock:
                    if self._latest_frame is not None:
                        self._dropped_frames += 1
                    self._latest_frame = frame
                    self._last_frame_timestamp = now
                    self._total_frames_received += 1
                    self._state = CameraState.STREAMING

            except Exception as e:
                logger.error(f"Error reading frame from RTSP stream [{self.camera_id}]: {e}")
                self._state = CameraState.ERROR
                if self._cap is not None:
                    try:
                        self._cap.release()
                    except Exception:
                        pass
                    self._cap = None

        # Clean shutdown
        if self._cap is not None:
            try:
                self._cap.release()
            except Exception:
                pass
            self._cap = None
        self._state = CameraState.STOPPED
        logger.info(f"RTSP grabber thread for [{self.camera_id}] exited cleanly.")

    def read_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Non-blocking read of the latest frame from the background buffer.
        
        Returns:
            (success: bool, frame: np.ndarray | None)
        """
        now = time.time()
        with self._lock:
            # Check stale frame timeout if streaming
            if self._state == CameraState.STREAMING:
                if self._last_frame_timestamp > 0 and (now - self._last_frame_timestamp > self.stale_frame_timeout):
                    self._state = CameraState.STALE
                    logger.warning(
                        f"RTSP stream [{self.camera_id}] is STALE. "
                        f"No frame received for {now - self._last_frame_timestamp:.1f}s."
                    )

            if self._latest_frame is None or self._state in (CameraState.DISCONNECTED, CameraState.STOPPED, CameraState.ERROR):
                return False, None

            frame = self._latest_frame
            # Consume frame (clear buffer so subsequent reads detect fresh arrivals)
            self._latest_frame = None
            return True, frame

    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        """Alias for read_frame() conforming to BaseCameraSource."""
        return self.read_frame()

    def is_opened(self) -> bool:
        """
        Returns True if the camera worker is active and not stopped/disconnected.
        """
        return (
            self._worker_thread is not None
            and self._worker_thread.is_alive()
            and self._state != CameraState.STOPPED
            and self._state != CameraState.DISCONNECTED
        )

    def release(self) -> None:
        """
        Idempotent and safe teardown: stops grabber thread, releases VideoCapture,
        clears in-memory buffers, and joins the worker thread.
        """
        self._stop_event.set()
        
        if self._worker_thread is not None and self._worker_thread.is_alive():
            if threading.current_thread() != self._worker_thread:
                self._worker_thread.join(timeout=2.0)
            self._worker_thread = None

        with self._lock:
            if self._cap is not None:
                try:
                    self._cap.release()
                except Exception:
                    pass
                self._cap = None
            self._latest_frame = None
            self._state = CameraState.STOPPED

        logger.info(f"RTSP source [{self.camera_id}] released.")

    def health_status(self) -> dict[str, Any]:
        """
        Returns structured telemetry diagnostics without exposing credentials.
        """
        with self._lock:
            return {
                "camera_id": self.camera_id,
                "name": self.name,
                "sanitized_url": self._sanitized_url,
                "state": self._state.value,
                "resolution": (self._native_width, self._native_height),
                "fps": self._native_fps,
                "total_frames_received": self._total_frames_received,
                "dropped_frames": self._dropped_frames,
                "reconnect_count": self._reconnect_count,
                "consecutive_failures": self._consecutive_failures,
                "last_frame_timestamp": self._last_frame_timestamp,
            }

    @property
    def resolution(self) -> Tuple[int, int]:
        """Return current stream resolution (width, height)."""
        return (self._native_width, self._native_height)

    @property
    def fps(self) -> float:
        """Return native or configured frame rate."""
        return self._native_fps
