"""
Unit test suite for Phase 2.3A AI Accuracy Evaluation Framework.
Uses deterministic synthetic test fixtures with manually known ground truth.
"""

import json
import tempfile
import pytest

from ai.benchmarks.detection.evaluate_accuracy import (
    DetectionEvaluator,
    compute_iou,
    validate_dataset,
)


# Helper helper fixture generator for COCO GT dict
def make_gt_dataset(
    annotations: list[dict],
    width: int = 640,
    height: int = 480,
) -> dict:
    return {
        "images": [{"id": 1, "file_name": "test_01.jpg", "width": width, "height": height}],
        "categories": [
            {"id": 0, "name": "person", "supercategory": "person"},
            {"id": 2, "name": "car", "supercategory": "vehicle"},
            {"id": 3, "name": "motorcycle", "supercategory": "vehicle"},
            {"id": 5, "name": "bus", "supercategory": "vehicle"},
            {"id": 7, "name": "truck", "supercategory": "vehicle"},
        ],
        "annotations": annotations,
    }


# -----------------------------------------------------------------------------
# IoU Helper Function Tests
# -----------------------------------------------------------------------------
def test_compute_iou_exact_match() -> None:
    box = [100.0, 100.0, 200.0, 200.0]
    assert compute_iou(box, box) == 1.0


def test_compute_iou_no_overlap() -> None:
    box1 = [0.0, 0.0, 50.0, 50.0]
    box2 = [100.0, 100.0, 150.0, 150.0]
    assert compute_iou(box1, box2) == 0.0


def test_compute_iou_partial_overlap() -> None:
    box1 = [0.0, 0.0, 10.0, 10.0]  # Area = 100
    box2 = [5.0, 0.0, 15.0, 10.0]  # Area = 100, Intersection = 5x10 = 50, Union = 150
    assert pytest.approx(compute_iou(box1, box2), 0.01) == 0.3333


# -----------------------------------------------------------------------------
# Test A: 1 GT, 1 Correct Prediction (IoU >= 0.5) -> TP=1, FP=0, FN=0
# -----------------------------------------------------------------------------
def test_evaluator_test_a_perfect_match() -> None:
    gt = make_gt_dataset([{
        "id": 1,
        "image_id": 1,
        "category_id": 0,
        "bbox": [100, 100, 50, 100],  # [x, y, w, h] -> [100, 100, 150, 200]
    }])
    preds = [{
        "image_id": 1,
        "category_id": 0,
        "confidence": 0.92,
        "bbox": [100, 100, 150, 200],  # Exact match xyxy
    }]

    evaluator = DetectionEvaluator(iou_threshold=0.5)
    report = evaluator.evaluate_predictions(gt, preds)

    summary = report["overall_summary"]
    assert summary["true_positives"] == 1
    assert summary["false_positives"] == 0
    assert summary["false_negatives"] == 0
    assert summary["precision"] == 1.0
    assert summary["recall"] == 1.0
    assert summary["f1_score"] == 1.0


# -----------------------------------------------------------------------------
# Test B: 1 GT, 0 Predictions -> TP=0, FP=0, FN=1, Recall=0.0
# -----------------------------------------------------------------------------
def test_evaluator_test_b_missed_detection() -> None:
    gt = make_gt_dataset([{
        "id": 1,
        "image_id": 1,
        "category_id": 0,
        "bbox": [100, 100, 50, 100],
    }])
    preds: list[dict] = []

    evaluator = DetectionEvaluator(iou_threshold=0.5)
    report = evaluator.evaluate_predictions(gt, preds)

    summary = report["overall_summary"]
    assert summary["true_positives"] == 0
    assert summary["false_positives"] == 0
    assert summary["false_negatives"] == 1
    assert summary["precision"] == 0.0
    assert summary["recall"] == 0.0
    assert summary["f1_score"] == 0.0


# -----------------------------------------------------------------------------
# Test C: 0 GT, 1 Prediction -> TP=0, FP=1, FN=0, Precision=0.0
# -----------------------------------------------------------------------------
def test_evaluator_test_c_false_alarm() -> None:
    gt = make_gt_dataset([])
    preds = [{
        "image_id": 1,
        "category_id": 0,
        "confidence": 0.85,
        "bbox": [50, 50, 100, 100],
    }]

    evaluator = DetectionEvaluator(iou_threshold=0.5)
    report = evaluator.evaluate_predictions(gt, preds)

    summary = report["overall_summary"]
    assert summary["true_positives"] == 0
    assert summary["false_positives"] == 1
    assert summary["false_negatives"] == 0
    assert summary["precision"] == 0.0
    assert summary["recall"] == 0.0


# -----------------------------------------------------------------------------
# Test D: 1 GT, 1 Prediction (IoU < 0.5) -> TP=0, FP=1, FN=1
# -----------------------------------------------------------------------------
def test_evaluator_test_d_low_iou_mismatch() -> None:
    gt = make_gt_dataset([{
        "id": 1,
        "image_id": 1,
        "category_id": 0,
        "bbox": [0, 0, 100, 100],  # [0, 0, 100, 100]
    }])
    # Overlap is only 10x100 out of 19000 union -> IoU ~ 0.05 < 0.5
    preds = [{
        "image_id": 1,
        "category_id": 0,
        "confidence": 0.80,
        "bbox": [90, 0, 190, 100],
    }]

    evaluator = DetectionEvaluator(iou_threshold=0.5)
    report = evaluator.evaluate_predictions(gt, preds)

    summary = report["overall_summary"]
    assert summary["true_positives"] == 0
    assert summary["false_positives"] == 1
    assert summary["false_negatives"] == 1
    assert summary["precision"] == 0.0
    assert summary["recall"] == 0.0


# -----------------------------------------------------------------------------
# Test E: Multi-Class Accounting (person, car, truck)
# -----------------------------------------------------------------------------
def test_evaluator_test_e_multiclass_breakdown() -> None:
    gt = make_gt_dataset([
        {"id": 1, "image_id": 1, "category_id": 0, "bbox": [10, 10, 50, 50]},  # Person GT
        {"id": 2, "image_id": 1, "category_id": 2, "bbox": [200, 200, 100, 100]},  # Car GT
    ])
    preds = [
        {"image_id": 1, "category_id": 0, "confidence": 0.9, "bbox": [10, 10, 60, 60]},  # Person TP
        {"image_id": 1, "category_id": 7, "confidence": 0.8, "bbox": [400, 400, 500, 500]},  # Truck FP
    ]

    evaluator = DetectionEvaluator(iou_threshold=0.5)
    report = evaluator.evaluate_predictions(gt, preds)

    per_class = report["per_class_results"]
    assert per_class["person"]["true_positives"] == 1
    assert per_class["car"]["false_negatives"] == 1
    assert per_class["truck"]["false_positives"] == 1


# -----------------------------------------------------------------------------
# Test F: Duplicate Prediction Handling
# -----------------------------------------------------------------------------
def test_evaluator_test_f_duplicate_predictions() -> None:
    gt = make_gt_dataset([{
        "id": 1,
        "image_id": 1,
        "category_id": 0,
        "bbox": [100, 100, 50, 50],
    }])
    preds = [
        {"image_id": 1, "category_id": 0, "confidence": 0.95, "bbox": [100, 100, 150, 150]},  # Match 1 (TP)
        {"image_id": 1, "category_id": 0, "confidence": 0.80, "bbox": [100, 100, 150, 150]},  # Duplicate (FP)
    ]

    evaluator = DetectionEvaluator(iou_threshold=0.5)
    report = evaluator.evaluate_predictions(gt, preds)

    per_class = report["per_class_results"]
    assert per_class["person"]["true_positives"] == 1
    assert per_class["person"]["false_positives"] == 1


# -----------------------------------------------------------------------------
# Test G: Malformed Dataset Validation
# -----------------------------------------------------------------------------
def test_dataset_validation_failures() -> None:
    # 1. Non-positive width/height
    bad_gt = make_gt_dataset([{
        "id": 1,
        "image_id": 1,
        "category_id": 0,
        "bbox": [10, 10, -5, 50],
    }])
    is_valid, errors = validate_dataset(bad_gt)
    assert is_valid is False
    assert any("non-positive" in err for err in errors)

    # 2. Out of image bounds
    out_bounds_gt = make_gt_dataset([{
        "id": 1,
        "image_id": 1,
        "category_id": 0,
        "bbox": [10, 10, 1000, 1000],  # Image is 640x480
    }])
    is_valid_bounds, errors_bounds = validate_dataset(out_bounds_gt)
    assert is_valid_bounds is False
    assert any("extends outside image" in err for err in errors_bounds)

    # Evaluator raises ValueError on malformed dataset
    evaluator = DetectionEvaluator()
    with pytest.raises(ValueError, match="Dataset validation failed"):
        evaluator.evaluate_predictions(bad_gt, [])


# -----------------------------------------------------------------------------
# Test H: Results Serialization & Reproducibility Metadata
# -----------------------------------------------------------------------------
def test_results_serialization_and_metadata() -> None:
    gt = make_gt_dataset([{
        "id": 1,
        "image_id": 1,
        "category_id": 0,
        "bbox": [50, 50, 50, 50],
    }])
    preds = [{
        "image_id": 1,
        "category_id": 0,
        "confidence": 0.88,
        "bbox": [50, 50, 100, 100],
    }]

    evaluator = DetectionEvaluator()
    report = evaluator.evaluate_predictions(
        gt,
        preds,
        dataset_meta={
            "dataset_identifier": "SYNTHETIC_BENCHMARK_SET_01",
            "dataset_version": "1.0.0",
        },
    )

    with tempfile.NamedTemporaryFile(suffix=".json", mode="w+", delete=False) as tmp:
        saved_path = evaluator.save_results(report, output_path=tmp.name)
        with open(saved_path, "r", encoding="utf-8") as f:
            data = json.load(f)

    assert data["metadata"]["dataset_identifier"] == "SYNTHETIC_BENCHMARK_SET_01"
    assert "timestamp" in data["metadata"]
    assert "overall_summary" in data
    assert data["overall_summary"]["true_positives"] == 1
