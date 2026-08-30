"""Unit tests for AI Model Integrity & SHA-256 Checksum Verification."""

import hashlib
import tempfile
from unittest.mock import patch, MagicMock
import pytest

from ai.detection.detector import YOLODetector, compute_file_sha256
from ai.tracking.tracker import ByteTracker


def test_compute_file_sha256():
    """Verify compute_file_sha256 computes correct deterministic hex digest."""
    with tempfile.NamedTemporaryFile(suffix=".pt", delete=True) as tmp:
        tmp.write(b"mock-yolo-weights-binary-data")
        tmp.flush()

        expected_hash = hashlib.sha256(b"mock-yolo-weights-binary-data").hexdigest().lower()
        actual_hash = compute_file_sha256(tmp.name)
        assert actual_hash == expected_hash


def test_yolo_detector_checksum_verification_success():
    """Verify YOLODetector initializes cleanly when model checksum matches expected hash."""
    with tempfile.NamedTemporaryFile(suffix=".pt", delete=True) as tmp:
        tmp.write(b"valid-model-weights-content")
        tmp.flush()

        valid_sha = hashlib.sha256(b"valid-model-weights-content").hexdigest().lower()

        with patch("ai.detection.detector.YOLO") as mock_yolo:
            detector = YOLODetector(
                model_path=tmp.name,
                expected_sha256=valid_sha,
            )
            assert detector is not None
            mock_yolo.assert_called_once_with(tmp.name)


def test_yolo_detector_checksum_verification_mismatch_fails_closed():
    """Verify YOLODetector raises RuntimeError when local model hash doesn't match expected hash."""
    with tempfile.NamedTemporaryFile(suffix=".pt", delete=True) as tmp:
        tmp.write(b"tampered-model-weights-content")
        tmp.flush()

        wrong_sha = "0000000000000000000000000000000000000000000000000000000000000000"

        with patch("ai.detection.detector.YOLO"):
            with pytest.raises(RuntimeError, match="Model integrity verification failed"):
                YOLODetector(
                    model_path=tmp.name,
                    expected_sha256=wrong_sha,
                )


def test_bytetracker_checksum_verification_mismatch_fails_closed():
    """Verify ByteTracker raises RuntimeError when local model hash is mismatched."""
    with tempfile.NamedTemporaryFile(suffix=".pt", delete=True) as tmp:
        tmp.write(b"tampered-tracker-weights")
        tmp.flush()

        wrong_sha = "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"

        with patch("ai.tracking.tracker.YOLO"):
            with pytest.raises(RuntimeError, match="Model integrity verification failed"):
                ByteTracker(
                    model_path=tmp.name,
                    expected_sha256=wrong_sha,
                )
