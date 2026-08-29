"""Unit tests for YOLODetector."""

from unittest.mock import MagicMock, patch

import numpy as np
import torch

from ai.detection.detector import YOLODetector


def test_detector_initialization_defaults() -> None:
    with patch("ai.detection.detector.YOLO") as mock_yolo:
        detector = YOLODetector(model_path="yolov8n.pt", confidence_threshold=0.4)
        mock_yolo.assert_called_once_with("yolov8n.pt")
        assert detector.confidence_threshold == 0.4
        assert detector.target_classes == {0, 2, 3, 5, 7}


def test_detector_custom_classes() -> None:
    with patch("ai.detection.detector.YOLO"):
        detector = YOLODetector(target_classes={0})
        assert detector.target_classes == {0}


def test_detector_filters_classes_and_formats_output() -> None:
    with patch("ai.detection.detector.YOLO") as mock_yolo:
        mock_model_instance = MagicMock()
        mock_yolo.return_value = mock_model_instance

        # Mock predict output
        mock_result = MagicMock()
        mock_result.names = {0: "person", 2: "car", 15: "cat"}

        # 3 boxes: 1 person (target), 1 car (target), 1 cat (ignored)
        mock_boxes = MagicMock()
        mock_boxes.__len__.return_value = 3
        mock_boxes.cls = [torch.tensor(0), torch.tensor(2), torch.tensor(15)]
        mock_boxes.conf = [torch.tensor(0.88), torch.tensor(0.92), torch.tensor(0.99)]
        mock_boxes.xyxy = [
            torch.tensor([10.0, 20.0, 50.0, 100.0]),
            torch.tensor([100.0, 150.0, 300.0, 400.0]),
            torch.tensor([5.0, 5.0, 25.0, 25.0]),
        ]

        mock_result.boxes = mock_boxes
        mock_model_instance.predict.return_value = [mock_result]

        detector = YOLODetector(confidence_threshold=0.35)
        dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        detections = detector.detect(dummy_frame)

        assert len(detections) == 2

        # Verify person detection
        assert detections[0].class_id == 0
        assert detections[0].class_name == "person"
        assert round(detections[0].confidence, 2) == 0.88
        assert detections[0].bbox == [10.0, 20.0, 50.0, 100.0]

        # Verify car detection
        assert detections[1].class_id == 2
        assert detections[1].class_name == "car"
        assert round(detections[1].confidence, 2) == 0.92
        assert detections[1].bbox == [100.0, 150.0, 300.0, 400.0]


def test_detector_empty_boxes() -> None:
    with patch("ai.detection.detector.YOLO") as mock_yolo:
        mock_model_instance = MagicMock()
        mock_yolo.return_value = mock_model_instance

        mock_result = MagicMock()
        mock_result.boxes = None
        mock_model_instance.predict.return_value = [mock_result]

        detector = YOLODetector()
        dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        detections = detector.detect(dummy_frame)

        assert detections == []
