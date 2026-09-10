# IBVAP Object Detection Specification

**Module:** `ai/detection/detector.py`  
**Model Architecture:** Ultralytics YOLOv8 nano (`yolov8n.pt` / `yolov8n.onnx`)  
**Default Confidence Threshold:** `0.35`  
**Input Format:** OpenCV BGR `np.ndarray` (H x W x 3, `dtype=uint8`)  

---

## 1. Target Classes

IBVAP filters raw COCO 80-class detections down to surveillance-relevant targets:

| Class ID | Class Name | Category | Primary Use Case |
| :---: | :--- | :--- | :--- |
| **0** | `person` | Human Intruder | Border perimeter intrusion detection |
| **2** | `car` | Vehicle | Unauthorized vehicle crossing |
| **3** | `motorcycle`| Vehicle | Rapid off-road perimeter transit |
| **5** | `bus` | Heavy Vehicle | Vehicle convoy tracking |
| **7** | `truck` | Heavy Vehicle | Smuggling / transport detection |

Non-target classes (animals, birds, background movement) are immediately discarded, preventing false positive alarms.

---

## 2. Model Security & Weight Checksum

To prevent supply-chain model tampering, `ai/detection/detector.py` supports optional SHA-256 verification via `AI_MODEL_SHA256`:
- On initialization, the detector computes `hashlib.sha256(open(model_path, 'rb').read()).hexdigest()`.
- If configured and the hash does not match, the pipeline fails closed with a `SecurityError`.
