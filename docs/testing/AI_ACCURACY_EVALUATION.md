# IBVAP — AI Detection Accuracy Evaluation Framework Documentation

## 1. Overview

The **AI Detection Accuracy Evaluation Framework** provides reproducible, ground-truth benchmarking for IBVAP's object detection pipeline.

It reads human-annotated ground-truth bounding box datasets in standard **COCO JSON** format, matches model predictions against ground truth using **Intersection over Union (IoU)**, and calculates statistical metrics:
- True Positives (TP), False Positives (FP), False Negatives (FN)
- Precision, Recall, F1-Score
- mAP@0.5 and mAP@0.5:0.95
- Per-class metric breakdowns (`person`, `car`, `motorcycle`, `bus`, `truck`)
- Machine-readable reproducibility JSON metadata export

---

## 2. Directory Structure & File Conventions

Evaluation datasets, annotations, predictions, and benchmark results are structured as follows:

```
data/
  accuracy/
    images/           # Target evaluation images (.jpg, .png)
    annotations/      # COCO format ground-truth JSON files (e.g. instances_val.json)
    predictions/      # Model predictions JSON files
    results/          # Machine-readable output evaluation reports (detection_metrics.json)
```

---

## 3. Ground-Truth Annotation Format (COCO JSON)

Ground-truth datasets must conform to standard COCO JSON format:

```json
{
  "images": [
    {"id": 1, "file_name": "frame_001.jpg", "width": 1280, "height": 720}
  ],
  "categories": [
    {"id": 0, "name": "person", "supercategory": "person"},
    {"id": 2, "name": "car", "supercategory": "vehicle"},
    {"id": 3, "name": "motorcycle", "supercategory": "vehicle"},
    {"id": 5, "name": "bus", "supercategory": "vehicle"},
    {"id": 7, "name": "truck", "supercategory": "vehicle"}
  ],
  "annotations": [
    {
      "id": 1,
      "image_id": 1,
      "category_id": 0,
      "bbox": [100.0, 150.0, 50.0, 120.0],
      "area": 6000.0,
      "iscrowd": 0
    }
  ]
}
```

*Note: In COCO format, `bbox` is specified as `[x_min, y_min, width, height]` in pixel units.*

---

## 4. Evaluator API & Command Line Usage

### Programmatic API Usage
```python
from ai.benchmarks.detection.evaluate_accuracy import DetectionEvaluator

evaluator = DetectionEvaluator(iou_threshold=0.5)

# Evaluate predictions against ground truth
report = evaluator.evaluate_predictions(
    ground_truth=gt_coco_dict,
    predictions=predictions_list,
    dataset_meta={
        "dataset_identifier": "BORDER_PERIMETER_VAL_SET_01",
        "dataset_version": "1.0.0",
        "model_name": "YOLOv8n",
        "model_weights": "yolov8n.pt",
        "confidence_threshold": 0.35,
    }
)

# Export machine-readable JSON results
evaluator.save_results(report, output_path="data/accuracy/results/detection_metrics.json")
```

---

## 5. Mathematical Metric Definitions

* **Intersection over Union (IoU):**
  $$\text{IoU} = \frac{\text{Area}(\text{Box}_{\text{pred}} \cap \text{Box}_{\text{gt}})}{\text{Area}(\text{Box}_{\text{pred}} \cup \text{Box}_{\text{gt}})}$$

* **True Positive (TP):** Prediction matching an unmatched ground-truth box with $\text{IoU} \ge 0.50$.
* **False Positive (FP):** Prediction with $\text{IoU} < 0.50$, or duplicate prediction on an already matched ground-truth box.
* **False Negative (FN):** Ground-truth box with no matching prediction ($\text{IoU} < 0.50$).

* **Precision:** $\text{TP} / (\text{TP} + \text{FP})$
* **Recall:** $\text{TP} / (\text{TP} + \text{FN})$
* **F1-Score:** $2 \cdot (\text{Precision} \cdot \text{Recall}) / (\text{Precision} + \text{Recall})$

---

## 6. Synthetic Test Validation

The accuracy evaluator framework is validated using deterministic synthetic unit tests (`ai/tests/benchmarks/test_accuracy_evaluator.py`) covering:
- Perfect match ($\text{IoU} \ge 0.5 \implies \text{TP}=1, \text{FP}=0, \text{FN}=0$)
- Missed ground-truth box ($\implies \text{FN}=1$)
- False alarm prediction ($\implies \text{FP}=1$)
- Low IoU mismatch ($\text{IoU} < 0.5 \implies \text{FP}=1, \text{FN}=1$)
- Duplicate prediction handling
- Malformed annotation schema detection

---

## 7. Current Project Status & Disclaimer

> [!IMPORTANT]
> **No project-specific detection accuracy has yet been established.**
> The repository currently contains no human-annotated ground-truth dataset for border surveillance. Synthetic test fixtures validate software evaluator correctness, but real-world precision and recall metrics will be published once an annotated dataset is provided in a future phase.
