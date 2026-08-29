"""Unit tests for camera source abstraction module."""

from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from ai.camera.file import VideoFileSource
from ai.camera.synthetic import SyntheticSource
from ai.camera.webcam import WebcamSource


def test_webcam_source_open_and_read() -> None:
    with patch("ai.camera.webcam.cv2.VideoCapture") as mock_cap_class:
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, np.zeros((480, 640, 3), dtype=np.uint8))
        mock_cap.get.side_effect = lambda prop: 640.0 if prop == 3 else (480.0 if prop == 4 else 30.0)
        mock_cap_class.return_value = mock_cap

        with WebcamSource(camera_id="cam-01", camera_index=0) as source:
            assert source.is_opened() is True
            ok, frame = source.read_frame()
            assert ok is True
            assert frame is not None
            assert frame.shape == (480, 640, 3)
            assert source.resolution == (640, 480)
            assert source.fps == 30.0

        mock_cap.release.assert_called_once()


def test_webcam_source_failed_open() -> None:
    with patch("ai.camera.webcam.cv2.VideoCapture") as mock_cap_class:
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = False
        mock_cap_class.return_value = mock_cap

        source = WebcamSource(camera_index=99)
        with pytest.raises(RuntimeError, match="Failed to open webcam index 99"):
            source.open()


def test_video_file_source_not_found() -> None:
    source = VideoFileSource(file_path="/non/existent/video.mp4")
    with pytest.raises(FileNotFoundError):
        source.open()


def test_video_file_source_read_and_loop() -> None:
    with patch("os.path.exists", return_value=True):
        with patch("ai.camera.file.cv2.VideoCapture") as mock_cap_class:
            mock_cap = MagicMock()
            mock_cap.isOpened.return_value = True

            # Return a valid frame, then EOF (False), then loop (True)
            dummy = np.zeros((480, 640, 3), dtype=np.uint8)
            mock_cap.read.side_effect = [(True, dummy), (False, None), (True, dummy)]
            mock_cap_class.return_value = mock_cap

            source = VideoFileSource(file_path="dummy.mp4", loop=True)
            source.open()

            # Frame 1: valid
            ok1, f1 = source.read_frame()
            assert ok1 is True

            # Frame 2: EOF triggered -> rewound to frame 0 -> returns valid frame
            ok2, f2 = source.read_frame()
            assert ok2 is True
            mock_cap.set.assert_called_with(1, 0)  # CAP_PROP_POS_FRAMES = 1

            source.release()
            mock_cap.release.assert_called_once()


def test_synthetic_source_iteration() -> None:
    source = SyntheticSource(width=320, height=240, max_frames=5)
    frames = list(source)
    assert len(frames) == 5
    for f in frames:
        assert f.shape == (240, 320, 3)
