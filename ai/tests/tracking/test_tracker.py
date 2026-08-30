"""Unit tests for ByteTracker."""

from unittest.mock import MagicMock, patch

import numpy as np

try:
    import torch
except ImportError:
    class MockTensor:
        def __init__(self, val):
            self._val = val
        def cpu(self):
            return self
        def tolist(self):
            return self._val if isinstance(self._val, list) else [self._val]
        def item(self):
            return self._val
        def __int__(self):
            return int(self._val)
        def __float__(self):
            return float(self._val)

    class TorchMock:
        @staticmethod
        def tensor(val):
            return MockTensor(val)

    torch = TorchMock()  # type: ignore

from ai.tracking.tracker import ByteTracker



def test_bytetracker_initialization() -> None:
    with patch("ai.tracking.tracker.YOLO") as mock_yolo:
        tracker = ByteTracker(model_path="yolov8n.pt", confidence_threshold=0.5)
        mock_yolo.assert_called_once_with("yolov8n.pt")
        assert tracker.tracker_config == "bytetrack.yaml"
        assert tracker.confidence_threshold == 0.5
        assert tracker.target_classes == {0, 2, 3, 5, 7}


def test_bytetracker_track_with_ids() -> None:
    with patch("ai.tracking.tracker.YOLO") as mock_yolo:
        mock_model = MagicMock()
        mock_yolo.return_value = mock_model

        mock_result = MagicMock()
        mock_result.names = {0: "person", 2: "car", 16: "dog"}

        mock_boxes = MagicMock()
        mock_boxes.__len__.return_value = 2
        mock_boxes.cls = [torch.tensor(0), torch.tensor(16)]
        mock_boxes.id = [torch.tensor(101), torch.tensor(102)]
        mock_boxes.conf = [torch.tensor(0.95), torch.tensor(0.80)]
        mock_boxes.xyxy = [
            torch.tensor([50.0, 100.0, 150.0, 300.0]),
            torch.tensor([10.0, 20.0, 30.0, 40.0]),
        ]

        mock_result.boxes = mock_boxes
        mock_model.track.return_value = [mock_result]

        tracker = ByteTracker()
        dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        tracks = tracker.track(dummy_frame)

        # Dog (16) should be filtered out, person (0) kept
        assert len(tracks) == 1
        track = tracks[0]
        assert track.track_id == 101
        assert track.class_id == 0
        assert track.class_name == "person"
        assert round(track.confidence, 2) == 0.95
        assert track.bbox == [50.0, 100.0, 150.0, 300.0]
        assert track.reference_point == (100.0, 300.0)


def test_bytetracker_track_without_ids() -> None:
    with patch("ai.tracking.tracker.YOLO") as mock_yolo:
        mock_model = MagicMock()
        mock_yolo.return_value = mock_model

        mock_result = MagicMock()
        mock_result.names = {0: "person"}

        mock_boxes = MagicMock()
        mock_boxes.__len__.return_value = 1
        mock_boxes.cls = [torch.tensor(0)]
        mock_boxes.id = None  # Tracker hasn't assigned ID yet
        mock_boxes.conf = [torch.tensor(0.75)]
        mock_boxes.xyxy = [torch.tensor([10.0, 20.0, 30.0, 40.0])]

        mock_result.boxes = mock_boxes
        mock_model.track.return_value = [mock_result]

        tracker = ByteTracker()
        dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        tracks = tracker.track(dummy_frame)

        assert len(tracks) == 1
        assert tracks[0].track_id == -1


def test_bytetracker_reset() -> None:
    with patch("ai.tracking.tracker.YOLO") as mock_yolo:
        mock_model = MagicMock()
        mock_yolo.return_value = mock_model
        mock_model.predictor = MagicMock()
        mock_model.predictor.trackers = ["tracker1"]

        tracker = ByteTracker()
        tracker.reset()
        assert mock_model.predictor.trackers is None
