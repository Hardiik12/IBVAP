# IBVAP — M2 AI Computer Vision & Live Event Dispatch Engine

The `ai/` module contains the complete computer vision ingestion, object detection, multi-object tracking, spatial polygon zone logic, and live M1 backend event dispatching foundation for the **Intelligent Border Video Analytics Platform (IBVAP)**.

---

## 🏗️ Unified Pipeline Architecture

```
Camera Ingestion (Webcam / File)
      │ (BGR Frame)
      ▼
FrameProcessor (Validation, Resize, FPS calculation)
      │
      ▼
YOLOv8 Object Detector (Ultralytics nano)
      │
      ▼
ByteTrack Multi-Object Tracker (Persistent Track IDs)
      │ (Track with Foot Reference Point: ((x1+x2)/2, y2))
      ▼
Polygon Zone Engine (cv2.pointPolygonTest containment)
      │ (Zone State: OUTSIDE / INSIDE)
      ▼
Intrusion Event Engine (Positive transition OUTSIDE -> INSIDE + Duplicate Suppression)
      │ (EventPayload with Base64 JPEG snapshot)
      ▼
EventDispatcher (Authenticated HTTP POST /api/v1/events with JWT + Bounded Retry)
      │
      ▼
M1 FastAPI Backend (Database Persistence -> Alerts -> WebSockets -> Tactical HUD)
```

---

## ⚙️ Configuration Options

Configuration is managed via Pydantic `BaseSettings` ([`ai/core/config.py`](file:///Users/hardik/Downloads/IBVAP/ai/core/config.py)). Values can be overridden via environment variables or `.env` files prefixed with `AI_`.

| Variable | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `AI_SOURCE_TYPE` | `str` | `"WEBCAM"` | Input source (`WEBCAM` or `VIDEO_FILE`). |
| `AI_CAMERA_INDEX` | `int` | `0` | Device index for local/USB webcams (e.g. 0, 1). |
| `AI_VIDEO_PATH` | `str` | `None` | Path to local MP4/AVI file for `VIDEO_FILE` mode. |
| `AI_FRAME_WIDTH` | `int` | `None` | Optional target width for frame resizing. |
| `AI_FRAME_HEIGHT` | `int` | `None` | Optional target height for frame resizing. |
| `AI_DISPLAY_PREVIEW` | `bool` | `True` | Enable live OpenCV GUI window with overlays. |
| `AI_LOG_LEVEL` | `str` | `"INFO"` | Log verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`). |
| `AI_BACKEND_URL` | `str` | `"http://localhost:8000"` | Base URL of M1 FastAPI backend application. |
| `AI_USERNAME` | `str` | `"operator_user"` | Authentication username for acquiring JWT token. |
| `AI_PASSWORD` | `str` | `"OperatorSecret123!"`| Authentication password for acquiring JWT token. |
| `AI_CAMERA_ID` | `str` | `None` | Target Camera UUID in M1 backend database. |
| `AI_ZONE_ID` | `str` | `None` | Target Restricted Zone UUID in M1 backend database. |
| `AI_DISPATCH_TIMEOUT` | `float`| `5.0` | HTTP timeout in seconds for backend requests. |
| `AI_DISPATCH_RETRIES` | `int` | `3` | Maximum retry attempts on network error/5xx. |

---

## 🚀 Running the Unified Live Pipeline

### 1. Running Live Pipeline with Local Webcam
```bash
# Ensure virtualenv is active
python -m ai.pipeline.runner --source webcam --index 0
```
- Press **Q** or **ESC** while focusing the video preview window to cleanly release camera handles and exit.

### 2. Running Live Pipeline with Video File (Fallback Mode)
```bash
python -m ai.pipeline.runner --source video_file --path data/videos/test/sample_test.mp4
```

### 3. Running in Headless Server / CI Mode (`--headless`)
```bash
python -m ai.pipeline.runner --source video_file --path data/videos/test/sample_test.mp4 --headless
```

### 4. Running Ingestion-Only (No AI Inference / Diagnostic Test)
```bash
python -m ai.pipeline.runner --source webcam --no-ai
```

---

## 🧪 Running Automated Tests

```bash
# Run AI module test suite (70 tests)
backend/.venv/bin/pytest ai/tests/ -v

# Run full project regression suite (171 tests passing)
backend/.venv/bin/pytest backend/tests/ ai/tests/ -v
```

---

## 📊 Performance Benchmarks

* **Video Frame Ingestion Throughput**: **195.40 FPS** measured on standard video feed.
* **Spatial Polygon Check Latency**: $< 0.05 \text{ ms}$ per track.
* **Event Dispatch Latency**: $\approx 110\text{ ms}$ over HTTP to local FastAPI server with database and alert creation.
