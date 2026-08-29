import os
import tempfile
import pytest
import cv2
import numpy as np
from ai.camera.source import (
    WebcamSource,
    VideoFileSource,
    create_camera_source,
    BaseCameraSource
)


def test_factory_webcam_creation():
    """Test factory creates WebcamSource instance."""
    src = create_camera_source("WEBCAM", camera_index=0)
    assert isinstance(src, WebcamSource)
    assert src.camera_index == 0


def test_factory_video_file_creation():
    """Test factory creates VideoFileSource instance."""
    src = create_camera_source("VIDEO_FILE", video_path="data/test_videos/test.mp4")
    assert isinstance(src, VideoFileSource)
    assert src.video_path == "data/test_videos/test.mp4"


def test_factory_unsupported_source_type():
    """Test unsupported source type raises ValueError."""
    with pytest.raises(ValueError) as exc_info:
        create_camera_source("INVALID_SOURCE")
    assert "Unsupported SOURCE_TYPE" in str(exc_info.value)


def test_video_file_missing_path():
    """Test initializing VideoFileSource without path raises ValueError."""
    with pytest.raises(ValueError):
        VideoFileSource(video_path="")


def test_video_file_missing_file_on_disk():
    """Test opening a non-existent video file path raises FileNotFoundError."""
    src = VideoFileSource(video_path="non_existent_video_file_12345.mp4")
    with pytest.raises(FileNotFoundError):
        src.open()


def test_webcam_invalid_index_fails_open(monkeypatch):
    """Test opening an invalid webcam index raises RuntimeError cleanly using mock."""
    from unittest.mock import MagicMock
    mock_cap = MagicMock()
    mock_cap.isOpened.return_value = False
    monkeypatch.setattr(cv2, "VideoCapture", lambda idx: mock_cap)

    src = WebcamSource(camera_index=9999)
    with pytest.raises(RuntimeError) as exc_info:
        src.open()
    assert "Failed to open webcam at device index 9999" in str(exc_info.value)


def test_video_file_synthetic_reading(monkeypatch):
    """
    Test VideoFileSource correctly opens, reads frames, detects EOF, and releases
    using a mock VideoCapture stream feeding synthetic frames.
    """
    from unittest.mock import MagicMock
    num_frames = 10
    current_frame = 0

    mock_cap = MagicMock()
    mock_cap.isOpened.return_value = True

    def mock_read():
        nonlocal current_frame
        if current_frame < num_frames:
            current_frame += 1
            frame = np.zeros((240, 320, 3), dtype=np.uint8)
            return True, frame
        return False, None

    mock_cap.read.side_effect = mock_read

    # Create dummy file so os.path.exists passes
    with tempfile.NamedTemporaryFile(suffix=".mp4") as tmp_file:
        monkeypatch.setattr(cv2, "VideoCapture", lambda path: mock_cap)

        src = VideoFileSource(video_path=tmp_file.name)
        assert src.open() is True
        assert src.is_opened() is True

        read_count = 0
        while True:
            success, frame = src.read()
            if not success or frame is None:
                break
            read_count += 1
            assert frame.shape == (240, 320, 3)

        assert read_count == num_frames
        src.release()
        assert src.is_opened() is False


def test_source_context_manager(monkeypatch):
    """Test BaseCameraSource context manager (__enter__ / __exit__) opens and releases."""
    from unittest.mock import MagicMock
    mock_cap = MagicMock()
    mock_cap.isOpened.return_value = True
    monkeypatch.setattr(cv2, "VideoCapture", lambda idx: mock_cap)

    with WebcamSource(camera_index=0) as src:
        assert src.is_opened() is True
    assert src.is_opened() is False


def test_source_read_when_not_opened():
    """Test calling read() on un-opened sources returns False, None safely."""
    webcam = WebcamSource(camera_index=0)
    assert webcam.read() == (False, None)

    video = VideoFileSource(video_path="some_path.mp4")
    assert video.read() == (False, None)


def test_video_file_real_disk_reading():
    """Test VideoFileSource on a real video file generated in data/videos/test/."""
    video_path = "data/videos/test/sample_test.mp4"
    if not os.path.exists(video_path):
        pytest.skip("Test video file not present")

    src = VideoFileSource(video_path=video_path)
    src.open()
    assert src.is_opened() is True

    frame_count = 0
    while True:
        success, frame = src.read()
        if not success or frame is None:
            break
        frame_count += 1
        assert frame.ndim == 3
        assert frame.shape[0] == 720
        assert frame.shape[1] == 1280

    assert frame_count == 60
    src.release()
    assert src.is_opened() is False

