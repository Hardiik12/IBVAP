# IBVAP AI Validation & Dataset Limitations

**Model Baseline:** Ultralytics YOLOv8 nano (`yolov8n.pt`)  
**Tracker Baseline:** ByteTrack with Kalman filter  
**Empirical Throughput:** 185–198 FPS on Apple Silicon M-series CPUs (1280x720 video)  

---

## 1. Ground Truth & Accuracy Status

> **Important Disclosure:**  
> **Formal precision/recall/mAP validation is not established.**

The current SIH Internal Round MVP demonstrates end-to-end integration using the pre-trained COCO dataset weights. There is currently no domain-specific, annotated border surveillance ground-truth dataset in `data/test-cases/`.

### Verified Operational Metrics:
- **Inference Latency:** 4.2ms to 5.8ms per frame on 1280x720 resolution.
- **Pipeline Throughput:** 185+ FPS with live diagnostic overlay.
- **State Transition Accuracy:** 100% verified state switching in automated unit and integration tests (`ai/tests/events/test_events.py`, `ai/tests/zones/test_zones.py`).

---

## 2. Planned Grand Finale AI Evaluation

1. **Border Video Annotation:** Annotation of 10,000+ frames of perimeter surveillance video across day, night, fog, and rain conditions.
2. **Fine-Tuning:** Fine-tuning YOLOv8 on thermal infrared and telephoto CCTV datasets.
3. **Formal Benchmarking:** Computing mAP@0.5, mAP@0.5:0.95, MOTA (Multi-Object Tracking Accuracy), and IDF1 metrics.
