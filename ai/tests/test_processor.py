import time
import pytest
import numpy as np
from ai.camera.frame_processor import FrameProcessor, FPSCounter, FrameMetadata


def test_fps_counter_moving_average():
    """Test FPSCounter calculates positive FPS based on time intervals."""
    counter = FPSCounter(window_size=10)
    for _ in range(5):
        counter.update()
        time.sleep(0.01)
    fps = counter.update()
    assert fps > 0.0


def test_frame_processor_synthetic_frame():
    """Test processing a synthetic 1280x720 frame extracts valid metadata."""
    processor = FrameProcessor(source_type="WEBCAM")
    frame = np.zeros((720, 1280, 3), dtype=np.uint8)

    processed_frame, metadata, fps = processor.process(frame)

    assert processed_frame.shape == (720, 1280, 3)
    assert metadata.frame_id == 1
    assert metadata.width == 1280
    assert metadata.height == 720
    assert metadata.source_type == "WEBCAM"
    assert isinstance(metadata.timestamp, float)
    assert isinstance(fps, float)


def test_frame_processor_resizing():
    """Test FrameProcessor resizes frames when target dimensions are set."""
    processor = FrameProcessor(target_width=640, target_height=480, source_type="VIDEO_FILE")
    original_frame = np.zeros((720, 1280, 3), dtype=np.uint8)

    processed_frame, metadata, _ = processor.process(original_frame)

    assert processed_frame.shape == (480, 640, 3)
    assert metadata.width == 640
    assert metadata.height == 480
    assert metadata.source_type == "VIDEO_FILE"


def test_frame_processor_invalid_none_frame():
    """Test passing None to FrameProcessor raises ValueError."""
    processor = FrameProcessor()
    with pytest.raises(ValueError) as exc_info:
        processor.process(None)
    assert "Frame object is None" in str(exc_info.value)


def test_frame_processor_invalid_empty_array():
    """Test passing an empty array raises ValueError."""
    processor = FrameProcessor()
    empty_frame = np.zeros((0, 0, 3), dtype=np.uint8)
    with pytest.raises(ValueError) as exc_info:
        processor.process(empty_frame)
    assert "Invalid frame dimensions" in str(exc_info.value)


def test_frame_processor_invalid_ndim():
    """Test passing a 2D grayscale array or 1D array raises ValueError."""
    processor = FrameProcessor()
    invalid_2d_frame = np.zeros((720, 1280), dtype=np.uint8)
    with pytest.raises(ValueError) as exc_info:
        processor.process(invalid_2d_frame)
    assert "Invalid frame dimensions" in str(exc_info.value)


def test_frame_processor_non_numpy_input():
    """Test passing a non-numpy object raises ValueError."""
    processor = FrameProcessor()
    with pytest.raises(ValueError) as exc_info:
        processor.process("not_a_frame")  # type: ignore
    assert "not a numpy array" in str(exc_info.value)


def test_fps_counter_initial_values():
    """Test FPSCounter returns 0.0 when fewer than 2 timestamps are recorded."""
    counter = FPSCounter()
    assert counter.update() == 0.0

