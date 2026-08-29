"""Unit tests for detection schemas."""

from ai.detection.schemas import NormalizedDetection


def test_normalized_detection_instantiation() -> None:
    detection = NormalizedDetection(
        class_id=0,
        class_name="person",
        confidence=0.89,
        bbox=[100.0, 150.0, 200.0, 350.0],
    )
    assert detection.class_id == 0
    assert detection.class_name == "person"
    assert detection.confidence == 0.89
    assert detection.bbox == [100.0, 150.0, 200.0, 350.0]


def test_normalized_detection_to_dict() -> None:
    detection = NormalizedDetection(
        class_id=2,
        class_name="car",
        confidence=0.95,
        bbox=[50.0, 60.0, 300.0, 250.0],
    )
    data = detection.to_dict()
    assert data == {
        "class_id": 2,
        "class_name": "car",
        "confidence": 0.95,
        "bbox": [50.0, 60.0, 300.0, 250.0],
    }
