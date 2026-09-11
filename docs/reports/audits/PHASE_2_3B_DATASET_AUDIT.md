# IBVAP — Phase 2.3B Dataset & Ground-Truth Strategy Audit Report

**Audit Mode:** READ-ONLY RESEARCH & DATASET STRATEGY AUDIT  
**Project:** Intelligent Border Video Analytics Platform (IBVAP)  
**Branch:** `phase-2.3b-dataset-audit`  
**Date:** 2026-09-11  
**Status Baseline:** 🟢 **202/202 Automated Tests Passing**  

---

## 1. Audit Executive Summary

This read-only audit establishes the dataset and ground-truth strategy for evaluating IBVAP's object detection pipeline (`YOLOv8n`). It evaluates 5 public candidate datasets, specifies an annotation policy and leakage-safe data split, recommends an initial sample size for a project-specific border validation dataset, and defines dataset governance.

> [!IMPORTANT]
> **Read-Only Audit Disclaimer:**
> **No datasets were downloaded and no application code was modified during this audit.**
> The evaluation framework built in Phase 2.3A is ready to execute once a labeled dataset is provided. The official project status remains:
> *"No project-specific detection accuracy has yet been established."*

---

## 2. Public Dataset Comparative Evaluation Matrix

| Dataset | Primary Purpose | Camera Angle | Camera Motion | Target Classes | Night Coverage | License | IBVAP Suitability | Major Limitation |
| :--- | :--- | :--- | :--- | :--- | :---: | :--- | :---: | :--- |
| **COCO 2017** | General Detection | Consumer Eye-Level | Handheld | Person, Car, Motor, Bus, Truck | Low | CC-BY 4.0 | Reference Baseline | Lacks high-angle elevated CCTV perspective & border terrain. |
| **VisDrone 2021** | Aerial UAV Surveillance | High-Angle Overhead | Moving Drone | Pedestrian, People, Car, Bus, Van | High | Non-Commercial | **Recommended Public Baseline** | Moving drone camera introduces parallax not present in static CCTV. |
| **MOT17** | Multi-Person Tracking | Elevated Street CCTV | Static & Moving | Person (Pedestrian only) | Medium | Academic | Tracking Baseline | Lacks vehicle classes (`car`, `truck`, `bus`). |
| **UA-DETRAC** | Traffic Surveillance | Overpass CCTV | Fixed Static | Car, Bus, Van | High | Academic | Vehicle Baseline | Lacks person class (`person`). |
| **BDD100K** | Autonomous Driving | Windshield Dashcam | Moving Vehicle | Person, Car, Truck, Bus, Motor | High | BSD 3-Clause | Low | Dashcam perspective differs from static pole/tower CCTV. |

---

## 3. IBVAP Border Validation Dataset Specification

### Required Perimeter Scenarios (10 Categories):
1. **Daylight Clear Visibility** (Clear baseline)
2. **Dawn / Dusk Low Illumination** (Low contrast shadows)
3. **Nighttime IR / Low Light** (Infrared illuminator reflections & sensor noise)
4. **Rain & Dust Storms** (Atmospheric noise)
5. **Sun Glare & Reflections** (Direct lens reflections)
6. **Foliage & Fence Occlusion** (Subjects partially hidden behind brush/fence)
7. **Long-Distance Subjects** (Tiny silhouettes $>50$m away)
8. **Multiple Overlapping Subjects** (Group incursions)
9. **Patrol & Tactical Vehicles** (Cars, trucks, motorcycles)
10. **Empty Control Scenes** (0 subjects, for False Positive Rate measurement)

---

## 4. Annotation Policy & Data Split Strategy

### Annotation Policy (COCO JSON Format):
- **Classes:** `0: person`, `2: car`, `3: motorcycle`, `5: bus`, `7: truck`.
- **Bounding Boxes:** `[x_min, y_min, width, height]` tight fit.
- **Occlusion Threshold:** Annotate if $>20\%$ visible (`iscrowd: 0`). Mark $<10\times 10$ px or unidentifiable objects `iscrowd: 1`.

### Data Splitting Protocol:
- **Sequence-Based Split:** Split by independent video clip / camera location to prevent temporal data leakage.
- **Ratio:** $60\%$ Development/Validation, $40\%$ Held-Out Test Set.

---

## 5. Sample Size & Governance

- **Target Sample Size:** **1,000 annotated images** (~5,000 objects across 20 distinct video clips).
- **Governance:** Semantic dataset versioning (`v1.0.0`), SHA-256 checksums, non-PII compliance (face/plate blurring), strict isolation between public and internal validation scores.

---

## 6. Summary of Created & Modified Files

### Created:
- [`docs/research/AI_ACCURACY_DATASET_STRATEGY.md`](file:///Users/hardik/Downloads/IBVAP/docs/research/AI_ACCURACY_DATASET_STRATEGY.md)
- [`docs/reports/audits/PHASE_2_3B_DATASET_AUDIT.md`](file:///Users/hardik/Downloads/IBVAP/docs/reports/audits/PHASE_2_3B_DATASET_AUDIT.md)

### Modified / Application Code:
- **None.** 0 application, detector, backend, or frontend files modified.

---

## 7. Baseline & Regression Results

```text
Baseline Test Suite:   202/202 passed
Final Test Suite:      202/202 passed
Application Code:      0 lines modified
Git Branch:            phase-2.3b-dataset-audit
Git Status:            Clean (2 research/audit docs created under docs/)
```
