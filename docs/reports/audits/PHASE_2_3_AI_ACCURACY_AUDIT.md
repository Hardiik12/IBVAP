# IBVAP — Phase 2.3 AI Accuracy Validation Read-Only Audit Report

**Audit Mode:** READ-ONLY COMPREHENSIVE REPOSITORY AUDIT  
**Project:** Intelligent Border Video Analytics Platform (IBVAP)  
**Branch:** `main`  
**Date:** 2026-09-11  
**Status Baseline:** 🟢 **202/202 Automated Tests Passing**  

---

## 1. Executive Summary

This read-only audit establishes the empirical state of **AI object detection accuracy validation** for the IBVAP platform. It separates verified software capabilities and throughput benchmarks from unverified statistical accuracy claims, identifies the accuracy validation gap, and details the recommended evaluation methodology and dataset strategy for post-MVP evaluation.

> [!IMPORTANT]
> **Formal Accuracy Statement:**
> **No project-specific detection accuracy has been established.**
> The repository currently contains **0 labeled ground-truth images or annotations**. While the pipeline's software architecture, multi-object tracking continuity, and throughput (185–198 FPS) are empirically verified across 202 automated tests, statistical detection accuracy (mAP, Precision, Recall) on border surveillance footage has not been benchmarked.

---

## 2. Current AI Pipeline Inspection & Configuration

Inspection of [`ai/detection/detector.py`](file:///Users/hardik/Downloads/IBVAP/ai/detection/detector.py), [`ai/tracking/tracker.py`](file:///Users/hardik/Downloads/IBVAP/ai/tracking/tracker.py), [`ai/pipeline/runner.py`](file:///Users/hardik/Downloads/IBVAP/ai/pipeline/runner.py), and [`ai/core/config.py`](file:///Users/hardik/Downloads/IBVAP/ai/core/config.py) confirms the active production configuration:

| Component / Parameter | Verified Value | Source File |
| :--- | :--- | :--- |
| **Object Detection Model** | `YOLOv8n` (Ultralytics Nano) | [`ai/detection/detector.py:18`](file:///Users/hardik/Downloads/IBVAP/ai/detection/detector.py#L18) |
| **Model Weights File** | `yolov8n.pt` (Pre-trained COCO weights) | [`ai/detection/detector.py:18`](file:///Users/hardik/Downloads/IBVAP/ai/detection/detector.py#L18) |
| **Model Integrity Verification** | SHA-256 hash validation (optional `MODEL_SHA256`) | [`ai/detection/detector.py:48-66`](file:///Users/hardik/Downloads/IBVAP/ai/detection/detector.py#L48-L66) |
| **Confidence Threshold** | `0.35` (Configurable via `YOLO_CONFIDENCE`) | [`ai/detection/detector.py:19`](file:///Users/hardik/Downloads/IBVAP/ai/detection/detector.py#L19) |
| **NMS / IoU Threshold** | `0.7` (Ultralytics `model.predict()` default) | [`ai/detection/detector.py:92-96`](file:///Users/hardik/Downloads/IBVAP/ai/detection/detector.py#L92-L96) |
| **Target Filter Classes** | `{0, 2, 3, 5, 7}` (`0=person`, `2=car`, `3=motorcycle`, `5=bus`, `7=truck`) | [`ai/detection/detector.py:76-80`](file:///Users/hardik/Downloads/IBVAP/ai/detection/detector.py#L76-L80) |
| **Input Resolution** | `1280x720` (Native stream, resized to `640x640` by YOLO engine) | [`ai/pipeline/runner.py`](file:///Users/hardik/Downloads/IBVAP/ai/pipeline/runner.py) |
| **Multi-Object Tracking** | ByteTrack (`track_thresh=0.4`, `match_thresh=0.8`, `track_buffer=30`) | [`ai/tracking/tracker.py`](file:///Users/hardik/Downloads/IBVAP/ai/tracking/tracker.py) |
| **Geofencing Containment** | Shapely Point-in-Polygon on bottom-center foot-point `[x_center, y_max]` | [`ai/zones/engine.py`](file:///Users/hardik/Downloads/IBVAP/ai/zones/engine.py) |
| **State Machine** | State transition triggers `INTRUSION` on `OUTSIDE` $\to$ `INSIDE` transition | [`ai/events/engine.py`](file:///Users/hardik/Downloads/IBVAP/ai/events/engine.py) |

---

## 3. Dataset Audit & Ground-Truth Availability

Audit of the `data/` directory and test fixtures confirms:

```text
Dataset exists:                NO
Labels exist:                  NO
Bounding boxes exist:          NO
Classes with ground truth:     None
Train/validation/test split:   None
Number of labeled images:      0
Number of labeled objects:     0
```

> [!NOTE]
> The `data/videos/` and `data/test-cases/` subdirectories contain sample video clips and synthetic test frames used for live demonstrations and software regression tests. **None of these video streams contain human-annotated ground-truth bounding box labels.**

---

## 4. Current Test Coverage vs. Accuracy Validation

The test suite contains 202 automated tests (`ai/tests/` and `backend/tests/`).

### What Current Tests Validate (VERIFIED):
- **Model Initialization & Integrity:** Verifies YOLOv8n loads correctly and rejects tampered weight files.
- **Output Schema Correctness:** Verifies `detect()` returns valid `NormalizedDetection` objects (`class_id`, `class_name`, `confidence`, `bbox=[x1, y1, x2, y2]`).
- **Class & Confidence Filtering:** Verifies detections below `conf=0.35` or outside target classes `{0, 2, 3, 5, 7}` are filtered.
- **Tracking Continuity:** Verifies ByteTrack maintains persistent `track_id` assignments across synthetic video frames.
- **State Machine Correctness:** Verifies polygon containment logic emits `INTRUSION` events on boundary crossing.

### What Current Tests Do NOT Validate (ACCURACY GAP):
- Tests do **NOT** compare model predictions against human-annotated ground-truth bounding boxes.
- Tests do **NOT** calculate IoU overlap metrics, True Positives (TP), False Positives (FP), or False Negatives (FN).
- A test assertion stating `assert len(detections) > 0` verifies that **the detector executed and returned a detection**, but does **NOT** prove that **the detection was statistically correct**.

---

## 5. Existing Performance Benchmark Audit

The repository contains an automated performance benchmarking script:
[`ai/benchmarks/performance/benchmark_pipeline.py`](file:///Users/hardik/Downloads/IBVAP/ai/benchmarks/performance/benchmark_pipeline.py)

### Benchmark Audit Findings:
- **Throughput Measured:** `185.0 – 198.5 FPS` (Frames per second).
- **Execution Scope:** Measures full end-to-end local processing loop: OpenCV frame acquisition $\to$ YOLOv8n detection $\to$ ByteTrack tracking $\to$ Polygon PIP geofencing $\to$ Intrusion state machine evaluation.
- **Resolution & Source:** `1280x720` synthetic MJPEG test video (300 frames).
- **Hardware Context:** Measured on developer workstation CPU (Apple Silicon / x86_64 host).
- **Critical Distinction:** **Throughput (FPS) is a measure of processing speed, NOT detection accuracy.** Throughput cannot be substituted for mAP, Precision, or Recall.

---

## 6. Accuracy Validation Gap Analysis

To transition from pre-trained COCO baseline claims to domain-specific empirical validation, the following gaps must be addressed in post-MVP phases:

| Metric / Dimension | COCO Reference (Published) | Local IBVAP Repository Status | Gap / Required Action |
| :--- | :---: | :---: | :--- |
| **mAP@0.5** | `52.5%` | 🔴 **0% (Unmeasured)** | Requires ground-truth labeled validation dataset |
| **mAP@0.5:0.95** | `37.3%` | 🔴 **0% (Unmeasured)** | Requires IoU matching evaluation script |
| **Precision** | Unspecified | 🔴 **0% (Unmeasured)** | Requires counting True Positives vs False Positives |
| **Recall** | Unspecified | 🔴 **0% (Unmeasured)** | Requires counting True Positives vs Missed Ground Truth |
| **F1-Score** | Unspecified | 🔴 **0% (Unmeasured)** | Harmonic mean of Precision and Recall |
| **False Positive Rate** | Unspecified | 🔴 **0% (Unmeasured)** | Measured on empty border scene test footage |
| **False Negative Rate** | Unspecified | 🔴 **0% (Unmeasured)** | Measured under heavy occlusion / distance scenes |

---

## 7. Recommended Evaluation Methodology & Dataset Strategy

### Recommended Dataset Strategy:
1. **Public Baseline Benchmark Dataset:** Use a standardized public dataset such as **VisDrone**, **PASCAL VOC**, or **MOT17** to benchmark baseline YOLOv8n detection and ByteTrack tracking under aerial/surveillance camera angles.
2. **Project-Specific Border Surveillance Dataset:** Collect and annotate a domain-specific dataset tailored to border perimeter security:
   - **Target Classes:** `person` (border crosser/patrol), `vehicle` (patrol car/truck/motorcycle).
   - **Surveillance Conditions:** Daylight, twilight, low-light/night vision, foliage occlusion, distance (>50m), and empty border scenes (for False Positive Rate evaluation).

### Recommended Evaluation Metrics:
In future evaluation phases, the benchmark script (`ai/benchmarks/detection/evaluate_accuracy.py`) should use `pycocotools` to compute:
- **Precision:** $\text{TP} / (\text{TP} + \text{FP})$ at IoU threshold $0.5$.
- **Recall:** $\text{TP} / (\text{TP} + \text{FN})$ at IoU threshold $0.5$.
- **F1-Score:** $2 \cdot (\text{Precision} \cdot \text{Recall}) / (\text{Precision} + \text{Recall})$.
- **mAP@0.5 & mAP@0.5:0.95:** Mean Average Precision calculated across all target classes.

---

## 8. Summary of Created & Modified Files

### Created:
- [`docs/reports/audits/PHASE_2_3_AI_ACCURACY_AUDIT.md`](file:///Users/hardik/Downloads/IBVAP/docs/reports/audits/PHASE_2_3_AI_ACCURACY_AUDIT.md)

### Modified / Application Code:
- **None.** No application code, inference parameters, model weights, backend, or frontend files were modified.

---

## 9. Baseline & Final Test Results

```text
Baseline Test Suite:   202/202 passed
Final Test Suite:      202/202 passed
Application Code:      0 lines modified
Git Branch:            main
Git Status:            Clean (1 audit doc created under docs/)
```
