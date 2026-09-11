# IBVAP — AI Accuracy Dataset & Ground-Truth Strategy

## 1. Overview & Objectives

This document establishes the strategic roadmap for selecting public reference datasets and designing a domain-specific **IBVAP Border Surveillance Validation Dataset**. 

The strategy ensures that future evaluation of IBVAP's object detection pipeline (`YOLOv8n`) produces scientifically sound, leakage-safe metrics (Precision, Recall, F1, mAP@0.5, mAP@0.5:0.95) using our COCO-compatible evaluation framework ([`docs/testing/AI_ACCURACY_EVALUATION.md`](file:///Users/hardik/Downloads/IBVAP/docs/testing/AI_ACCURACY_EVALUATION.md)).

---

## 2. Public Dataset Comparative Analysis

We evaluated 5 major public computer vision datasets against IBVAP's active production requirements (`YOLOv8n`, target classes: `person` [0], `car` [2], `motorcycle` [3], `bus` [5], `truck` [7], confidence threshold: `0.35`).

| Dataset | Primary Purpose | Camera Perspective | Camera Motion | Target Classes | Night / Low Light | License | IBVAP Suitability | Major Limitations for Border CCTV |
| :--- | :--- | :--- | :--- | :--- | :---: | :--- | :---: | :--- |
| **COCO 2017** | General Object Detection | Eye-level / Consumer | Handheld / Unconstrained | Person, Car, Motorcycle, Bus, Truck | Low | CC-BY 4.0 | **Reference Baseline Only** | Lacks elevated CCTV perspective, fence occlusions, & border terrain. |
| **VisDrone 2021** | UAV Aerial Surveillance | High-Angle Overhead | Moving Drone | Pedestrian, People, Car, Van, Bus, Motor | High | Non-Commercial | **High (Surveillance Angle)** | Drone motion introduces parallax; non-commercial license. |
| **MOT17** | Multi-Person Tracking | Elevated Street / CCTV | Static & Moving | Person (Pedestrian only) | Medium | Academic | **Medium (Tracking Only)** | Vehicle classes (`car`, `truck`, `bus`) are absent. |
| **UA-DETRAC** | Traffic Surveillance | Fixed Overpass CCTV | Static Stationary | Car, Bus, Van | High | Academic | **Medium (Vehicle Only)** | Person class (`person`) is completely absent. |
| **BDD100K** | Autonomous Driving | Windshield Dashcam | Moving Vehicle | Person, Car, Truck, Bus, Motorcycle | High | BSD 3-Clause | **Low (Dashcam View)** | Dashcam perspective differs from static pole/tower CCTV. |

### Strategic Recommendation:
1. **Public Reference Baseline:** Select **VisDrone** (for high-angle person/vehicle detection) and **MOT17** (for multi-object tracking continuity) as external academic reference baselines.
2. **Domain-Specific Requirement:** A dedicated **IBVAP Border Surveillance Dataset** is necessary because no public dataset mirrors static border fence perimeters, long-distance silhouettes, and infrared border night vision.

---

## 3. IBVAP Project-Specific Dataset Specification

### Required Scenario Categories
A domain-specific validation dataset must sample 10 operational border conditions:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   IBVAP BORDER SURVEILLANCE SCENARIOS                  │
├──────────────────────────────────┬─────────────────────────────────────┤
│ 1. Daylight Clear Visibility     │ 6. Foliage & Fence Partial Occlusion│
│ 2. Dawn / Dusk Low Illumination  │ 7. Long-Distance Silhouettes (>50m) │
│ 3. Night IR / Low-Light Vision   │ 8. Multiple Overlapping Subjects    │
│ 4. Rain & Atmospheric Dust       │ 9. Patrol & Tactical Vehicles       │
│ 5. Sun Glare & Lens Reflection   │ 10. Empty Control Scenes (0 Subjects)│
└──────────────────────────────────┴─────────────────────────────────────┘
```

---

## 4. Annotation Policy & COCO Schema

To maintain compatibility with [`ai/benchmarks/detection/evaluate_accuracy.py`](file:///Users/hardik/Downloads/IBVAP/ai/benchmarks/detection/evaluate_accuracy.py), all annotations must follow standard **COCO JSON**:

### Class ID Mapping
- `0`: `person`
- `2`: `car`
- `3`: `motorcycle`
- `5`: `bus`
- `7`: `truck`

### Bounding Box Annotation Protocol
1. **Coordinate Format:** `[x_min, y_min, width, height]` in pixel units.
2. **Tight Fit:** Bounding boxes must tightly enclose the visible boundaries of the object.
3. **Partial Occlusion:** Annotate objects if $>20\%$ of the body or structure is visible. Set `iscrowd: 0`.
4. **Distant / Small Objects:** Annotate if $\ge 10\times 10$ pixels and humanly recognizable.
5. **Ignore Regions:** Mark heavily blurred or $<10\times 10$ px objects with `iscrowd: 1` to exclude them from False Positive penalties.
6. **Empty Scenes:** Control images with no target objects must contain 0 annotations to measure **False Positive Rate (FPR)**.

---

## 5. Leakage-Safe Data Splitting Strategy

> [!CAUTION]
> **Temporal Data Leakage Risk:**
> Randomly splitting consecutive video frames into train and test sets causes severe data leakage because adjacent frames are nearly identical.

### Recommended Sequence-Based Split Strategy:
- **Unit of Splitting:** Independent video clips / camera locations (not individual frames).
- **Split Ratio:** $60\%$ Development / Validation Set, $40\%$ Held-Out Final Evaluation Test Set.
- **Rules:** No video sequence or camera location present in Development may appear in the Final Test Set.

---

## 6. Target Sample Size & Engineering Rationale

* **Recommended Target:** **1,000 annotated frames** (~5,000 object instances across 20 distinct video clips).
* **Engineering Rationale:** 1,000 frames sampled across 20 diverse video clips provides a statistically representative sample of day, night, occlusion, and distance variations while keeping manual annotation effort realistic for team execution.

---

## 7. Dataset Governance & Provenance

1. **Version Control:** Semantic versioning (`IBVAP-Dataset-v1.0.0.json`) paired with SHA-256 integrity checksums.
2. **Privacy & Anonymization:** Automatic blurring of license plates and face close-ups to prevent PII retention.
3. **Strict License Isolation:** Public datasets (VisDrone, MOT17) and internal IBVAP validation datasets must be stored in separate directories and evaluated independently. **Never average public and private dataset accuracy metrics into a single score.**

---

## 8. Current Project Status Disclaimer

> [!IMPORTANT]
> **No project-specific detection accuracy has yet been established.**
> This document specifies dataset selection and annotation policies. No datasets have been downloaded, and no model evaluation numbers have been fabricated.
