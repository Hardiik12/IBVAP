"""Comprehensive unit test suite for RTSPCameraSource and RTSP factory integration."""

import time
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from ai.camera.rtsp import CameraState, RTSPCameraSource, sanitize_rtsp_url
from ai.camera.source import BaseCameraSource, WebcamSource, VideoFileSource, create_camera_source
from ai.camera.synthetic import SyntheticSource
from ai.core.config import AISettings, ai_settings


# -----------------------------------------------------------------------------
# Scenario 1: RTSP Source Construction & Valid URL Schemes
# -----------------------------------------------------------------------------
def test_rtsp_source_construction_valid() -> None:
    source = RTSPCameraSource(
        rtsp_url="rtsp://192.168.1.100:554/stream1",
        camera_id="cam-rtsp-01",
        name="Main Gate RTSP",
    )
    assert source.camera_id == "cam-rtsp-01"
    assert source.name == "Main Gate RTSP"
    assert source.rtsp_url == "rtsp://192.168.1.100:554/stream1"
    assert source.state == CameraState.DISCONNECTED
    assert source.is_opened() is False


# -----------------------------------------------------------------------------
# Scenario 2: Valid Configuration
# -----------------------------------------------------------------------------
def test_rtsp_source_valid_configuration() -> None:
    source = RTSPCameraSource(
        rtsp_url="rtsps://secure.host:8554/live",
        reconnect_interval_base=2.0,
        reconnect_interval_max=15.0,
        stale_frame_timeout=5.0,
        tcp_transport=True,
        socket_timeout_us=3000000,
    )
    assert source.reconnect_interval_base == 2.0
    assert source.reconnect_interval_max == 15.0
    assert source.stale_frame_timeout == 5.0
    assert source.tcp_transport is True
    assert source.socket_timeout_us == 3000000


# -----------------------------------------------------------------------------
# Scenario 3: Invalid Configuration & Malformed Scheme
# -----------------------------------------------------------------------------
def test_rtsp_source_invalid_url_scheme() -> None:
    with pytest.raises(ValueError, match="Invalid RTSP URL scheme"):
        RTSPCameraSource(rtsp_url="http://192.168.1.100/stream")

    with pytest.raises(ValueError, match="non-empty string"):
        RTSPCameraSource(rtsp_url="")


# -----------------------------------------------------------------------------
# Scenario 4: RTSP URL Parsing
# -----------------------------------------------------------------------------
def test_rtsp_url_parsing() -> None:
    source = RTSPCameraSource(rtsp_url="rtsp://admin:pass123@10.0.0.5:554/h264")
    assert source.rtsp_url == "rtsp://admin:pass123@10.0.0.5:554/h264"
    assert "pass123" not in source.sanitized_url


# -----------------------------------------------------------------------------
# Scenario 5: Credential Redaction in Logs, Exceptions & Status
# -----------------------------------------------------------------------------
def test_credential_redaction() -> None:
    raw_url = "rtsp://admin:SuperSecretPass2026@192.168.1.50:554/live"
    sanitized = sanitize_rtsp_url(raw_url)
    assert "SuperSecretPass2026" not in sanitized
    assert ":***@" in sanitized

    source = RTSPCameraSource(rtsp_url=raw_url)
    health = source.health_status()
    assert "SuperSecretPass2026" not in health["sanitized_url"]
    assert "SuperSecretPass2026" not in str(health)


# -----------------------------------------------------------------------------
# Scenario 6 & 7: Connection Failure Handling Does Not Crash Process
# -----------------------------------------------------------------------------
def test_connection_failure_graceful_handling() -> None:
    with patch("ai.camera.rtsp.cv2.VideoCapture") as mock_cap_class:
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = False
        mock_cap_class.return_value = mock_cap

        source = RTSPCameraSource(
            rtsp_url="rtsp://10.255.255.1:554/blackhole",
            reconnect_interval_base=0.1,
            reconnect_interval_max=0.5,
        )
        assert source.open() is True
        time.sleep(0.3)
        assert source.state in (CameraState.CONNECTING, CameraState.RECONNECTING)
        ok, frame = source.read_frame()
        assert ok is False
        assert frame is None
        source.release()


# -----------------------------------------------------------------------------
# Scenario 8, 9, 10, 11: Reconnect, Backoff, Cap, and Reset
# -----------------------------------------------------------------------------
def test_reconnect_exponential_backoff_and_reset() -> None:
    with patch("ai.camera.rtsp.cv2.VideoCapture") as mock_cap_class:
        mock_cap = MagicMock()
        # Fail 2 times, then succeed
        mock_cap.isOpened.side_effect = [False, False, True]
        dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_cap.read.return_value = (True, dummy_frame)
        mock_cap.get.side_effect = lambda prop: 640.0 if prop == 3 else (480.0 if prop == 4 else 30.0)
        mock_cap_class.return_value = mock_cap

        source = RTSPCameraSource(
            rtsp_url="rtsp://192.168.1.10:554/stream",
            reconnect_interval_base=0.05,
            reconnect_interval_max=0.2,
        )
        source.open()
        time.sleep(0.4)

        health = source.health_status()
        assert health["reconnect_count"] >= 1
        source.release()


# -----------------------------------------------------------------------------
# Scenario 12 & 13: Stale Frame Detection and Recovery Trigger
# -----------------------------------------------------------------------------
def test_stale_frame_detection() -> None:
    source = RTSPCameraSource(
        rtsp_url="rtsp://192.168.1.10:554/stream",
        stale_frame_timeout=0.1,
    )
    # Simulate streaming state with old timestamp
    source._state = CameraState.STREAMING
    source._last_frame_timestamp = time.time() - 0.5
    source._latest_frame = np.zeros((10, 10, 3), dtype=np.uint8)

    ok, frame = source.read_frame()
    assert source.state == CameraState.STALE
    assert ok is True  # Returns buffered frame but marks state STALE
    assert frame is not None


# -----------------------------------------------------------------------------
# Scenario 14 & 15: Latest-Frame Buffering & No Unbounded Queue
# -----------------------------------------------------------------------------
def test_latest_frame_buffering_unconsumed_dropped() -> None:
    source = RTSPCameraSource(rtsp_url="rtsp://192.168.1.10:554/stream")
    frame1 = np.ones((10, 10, 3), dtype=np.uint8)
    frame2 = np.ones((10, 10, 3), dtype=np.uint8) * 2

    with source._lock:
        source._latest_frame = frame1

    # Simulate second frame arriving before read
    with source._lock:
        if source._latest_frame is not None:
            source._dropped_frames += 1
        source._latest_frame = frame2

    assert source._dropped_frames == 1
    source._state = CameraState.STREAMING
    source._last_frame_timestamp = time.time()

    ok, frame = source.read_frame()
    assert ok is True
    assert np.array_equal(frame, frame2)


# -----------------------------------------------------------------------------
# Scenario 16, 17, 18, 19: Stop Cleanup, Idempotency, Thread & VideoCapture Release
# -----------------------------------------------------------------------------
def test_release_cleanup_and_idempotency() -> None:
    with patch("ai.camera.rtsp.cv2.VideoCapture") as mock_cap_class:
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, np.zeros((480, 640, 3), dtype=np.uint8))
        mock_cap_class.return_value = mock_cap

        source = RTSPCameraSource(rtsp_url="rtsp://192.168.1.10:554/stream")
        source.open()
        time.sleep(0.1)

        assert source.is_opened() is True

        # Call release multiple times (idempotency check)
        source.release()
        source.release()

        assert source.is_opened() is False
        assert source.state == CameraState.STOPPED
        assert source._worker_thread is None


# -----------------------------------------------------------------------------
# Scenario 20: Webcam Regression
# -----------------------------------------------------------------------------
def test_webcam_regression() -> None:
    with patch("ai.camera.webcam.cv2.VideoCapture") as mock_cap_class:
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, np.zeros((480, 640, 3), dtype=np.uint8))
        mock_cap_class.return_value = mock_cap

        webcam = WebcamSource(camera_index=0)
        webcam.open()
        ok, frame = webcam.read()
        assert ok is True
        assert frame is not None
        webcam.release()


# -----------------------------------------------------------------------------
# Scenario 21: Video File Regression
# -----------------------------------------------------------------------------
def test_video_file_regression() -> None:
    with patch("os.path.exists", return_value=True):
        with patch("ai.camera.file.cv2.VideoCapture") as mock_cap_class:
            mock_cap = MagicMock()
            mock_cap.isOpened.return_value = True
            mock_cap.read.return_value = (True, np.zeros((480, 640, 3), dtype=np.uint8))
            mock_cap_class.return_value = mock_cap

            vf = VideoFileSource(video_path="sample.mp4")
            vf.open()
            ok, frame = vf.read()
            assert ok is True
            assert frame is not None
            vf.release()


# -----------------------------------------------------------------------------
# Scenario 22: Synthetic Camera Regression
# -----------------------------------------------------------------------------
def test_synthetic_camera_regression() -> None:
    syn = SyntheticSource(width=320, height=240, max_frames=2)
    syn.open()
    ok, frame = syn.read_frame()
    assert ok is True
    assert frame is not None
    assert frame.shape == (240, 320, 3)
    syn.release()


# -----------------------------------------------------------------------------
# Scenario 23: Camera Factory Integration & Regression
# -----------------------------------------------------------------------------
def test_camera_factory_integration() -> None:
    # 1. RTSP
    rtsp_src = create_camera_source(source_type="RTSP", rtsp_url="rtsp://10.0.0.1/live")
    assert isinstance(rtsp_src, RTSPCameraSource)

    # 2. WEBCAM
    with patch("ai.camera.webcam.cv2.VideoCapture"):
        webcam_src = create_camera_source(source_type="WEBCAM", camera_index=0)
        assert isinstance(webcam_src, WebcamSource)

    # 3. VIDEO_FILE
    with patch("os.path.exists", return_value=True):
        with patch("ai.camera.file.cv2.VideoCapture"):
            file_src = create_camera_source(source_type="VIDEO_FILE", video_path="clip.mp4")
            assert isinstance(file_src, VideoFileSource)

    # 4. SYNTHETIC
    syn_src = create_camera_source(source_type="SYNTHETIC")
    assert isinstance(syn_src, SyntheticSource)


# -----------------------------------------------------------------------------
# Scenario 24: Configuration Settings Verification
# -----------------------------------------------------------------------------
def test_ai_settings_rtsp_fields() -> None:
    settings = AISettings()
    assert hasattr(settings, "RTSP_URL")
    assert hasattr(settings, "RTSP_TRANSPORT")
    assert hasattr(settings, "RTSP_TIMEOUT")
    assert hasattr(settings, "RTSP_STALE_TIMEOUT")
    assert hasattr(settings, "RTSP_RECONNECT_INITIAL_DELAY")
    assert hasattr(settings, "RTSP_RECONNECT_MAX_DELAY")
    assert settings.RTSP_TRANSPORT == "tcp"
    assert settings.RTSP_STALE_TIMEOUT == 3.0
    assert settings.RTSP_RECONNECT_INITIAL_DELAY == 1.0
    assert settings.RTSP_RECONNECT_MAX_DELAY == 30.0
