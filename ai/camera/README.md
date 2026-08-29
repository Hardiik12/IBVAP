# Camera Ingestion Module (`ai/camera`)

Responsible for video stream ingestion and camera source abstraction for the IBVAP platform.

## Owner
**M3 — Video/Edge Lead**

## Key Components
- **`CameraSource`** (`ai/camera/base.py`): Abstract base class establishing the frame acquisition contract (`read_frame()`, `release()`, context management, and frame iteration).
- **`WebcamSource`** (`ai/camera/webcam.py`): Ingests live streams from local laptop webcams or USB cameras via OpenCV `cv2.VideoCapture`.
- **`VideoFileSource`** (`ai/camera/file.py`): Sequential frame reader from recorded video files for reproducible testing and demonstration fallback.
- **`SyntheticSource`** (`ai/camera/synthetic.py`): Synthetic test frame generator for headless testing and CI/CD pipelines.

## Frame Contract
All camera sources return frames according to the unified contract:

```python
ok, frame = source.read_frame()
```

- **`ok`**: `bool` indicating whether the frame was successfully read.
- **`frame`**: `numpy.ndarray` in **OpenCV BGR** format (`shape: (H, W, 3)`, `dtype: uint8`), or `None` on failure / EOF.
- **Return Type**: `tuple[bool, np.ndarray | None]`

## Integration with Existing M2 AI Pipeline

The raw OpenCV BGR frame from M3 flows directly into the existing M2 `YOLODetector` / `AIPipeline`:

```python
from ai.camera.webcam import WebcamSource
from ai.detection.detector import YOLODetector

# 1. Initialize M3 camera source and M2 detector
camera = WebcamSource(camera_index=0)
detector = YOLODetector(confidence_threshold=0.35)

# 2. Acquire and process frames
with camera as stream:
    ok, frame = stream.read_frame()
    if ok and frame is not None:
        # Pass BGR frame directly to M2 detector
        detections = detector.detect(frame)
        for det in detections:
            print(det.to_dict())
```
