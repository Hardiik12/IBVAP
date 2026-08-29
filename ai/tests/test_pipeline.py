import os
import tempfile
import pytest
import cv2
import numpy as np
from ai.pipeline.runner import CameraPipelineRunner


from unittest.mock import MagicMock


def setup_mock_video_capture(monkeypatch, total_available_frames: int = 15, width: int = 320, height: int = 240):
    """Helper to mock cv2.VideoCapture feeding synthetic frames without OS codec delays."""
    current_frame = 0

    mock_cap = MagicMock()
    mock_cap.isOpened.return_value = True

    def mock_read():
        nonlocal current_frame
        if current_frame < total_available_frames:
            current_frame += 1
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            return True, frame
        return False, None

    mock_cap.read.side_effect = mock_read
    monkeypatch.setattr(cv2, "VideoCapture", lambda path_or_idx: mock_cap)
    return mock_cap


def test_pipeline_headless_synthetic_video(monkeypatch):
    """Test running the pipeline in headless mode (DISPLAY_PREVIEW=False) processes all frames cleanly."""
    with tempfile.NamedTemporaryFile(suffix=".mp4") as tmp_file:
        num_frames = 15
        setup_mock_video_capture(monkeypatch, total_available_frames=num_frames)

        runner = CameraPipelineRunner(
            source_type="VIDEO_FILE",
            video_path=tmp_file.name,
            display_preview=False
        )

        total_frames = runner.run()
        assert total_frames == num_frames
        assert runner.source.is_opened() is False


def test_pipeline_max_frames_limit(monkeypatch):
    """Test configuring max_frames stops processing early after N frames."""
    with tempfile.NamedTemporaryFile(suffix=".mp4") as tmp_file:
        setup_mock_video_capture(monkeypatch, total_available_frames=20)

        runner = CameraPipelineRunner(
            source_type="VIDEO_FILE",
            video_path=tmp_file.name,
            display_preview=False
        )

        total_frames = runner.run(max_frames=5)
        assert total_frames == 5
        assert runner.source.is_opened() is False


def test_pipeline_resource_cleanup_on_completion(monkeypatch):
    """Test camera resources are released on pipeline completion or exit."""
    with tempfile.NamedTemporaryFile(suffix=".mp4") as tmp_file:
        setup_mock_video_capture(monkeypatch, total_available_frames=5)

        runner = CameraPipelineRunner(
            source_type="VIDEO_FILE",
            video_path=tmp_file.name,
            display_preview=False
        )
        runner.run()
        assert runner.source.is_opened() is False


def test_pipeline_draw_diagnostic_overlay():
    """Test diagnostic overlay adds text annotations without mutating original dimensions."""
    runner = CameraPipelineRunner(source_type="WEBCAM", camera_index=0, display_preview=False)
    frame = np.zeros((720, 1280, 3), dtype=np.uint8)
    annotated = runner.draw_diagnostic_overlay(frame, current_fps=29.5, width=1280, height=720)

    assert annotated.shape == (720, 1280, 3)
    # Check that overlay modified some pixel values
    assert np.any(annotated > 0)


def test_pipeline_keyboard_shutdown_q(monkeypatch):
    """Test pressing 'q' breaks out of preview loop and releases resources."""
    with tempfile.NamedTemporaryFile(suffix=".mp4") as tmp_file:
        setup_mock_video_capture(monkeypatch, total_available_frames=20)
        monkeypatch.setattr(cv2, "imshow", lambda win, img: None)
        monkeypatch.setattr(cv2, "waitKey", lambda delay: ord('q'))
        monkeypatch.setattr(cv2, "destroyAllWindows", lambda: None)

        runner = CameraPipelineRunner(
            source_type="VIDEO_FILE",
            video_path=tmp_file.name,
            display_preview=True
        )

        total_frames = runner.run()
        assert total_frames == 1
        assert runner.source.is_opened() is False


def test_pipeline_keyboard_shutdown_esc(monkeypatch):
    """Test pressing ESC (27) breaks out of preview loop and releases resources."""
    with tempfile.NamedTemporaryFile(suffix=".mp4") as tmp_file:
        setup_mock_video_capture(monkeypatch, total_available_frames=20)
        monkeypatch.setattr(cv2, "imshow", lambda win, img: None)
        monkeypatch.setattr(cv2, "waitKey", lambda delay: 27)
        monkeypatch.setattr(cv2, "destroyAllWindows", lambda: None)

        runner = CameraPipelineRunner(
            source_type="VIDEO_FILE",
            video_path=tmp_file.name,
            display_preview=True
        )

        total_frames = runner.run()
        assert total_frames == 1
        assert runner.source.is_opened() is False


def test_pipeline_exception_cleanup(monkeypatch):
    """Test that unexpected processing exceptions still release the source properly."""
    with tempfile.NamedTemporaryFile(suffix=".mp4") as tmp_file:
        setup_mock_video_capture(monkeypatch, total_available_frames=5)

        runner = CameraPipelineRunner(
            source_type="VIDEO_FILE",
            video_path=tmp_file.name,
            display_preview=False
        )

        def faulty_process(frame):
            raise RuntimeError("Simulated unexpected frame processing failure")

        monkeypatch.setattr(runner.processor, "process", faulty_process)

        with pytest.raises(RuntimeError):
            runner.run()

        assert runner.source.is_opened() is False

