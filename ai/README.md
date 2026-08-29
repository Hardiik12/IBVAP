# IBVAP — M2 AI Computer Vision Module

The `ai/` module contains the computer vision ingestion and frame-processing foundation for the **Intelligent Border Video Analytics Platform (IBVAP)**.

---

## 🏗️ Module Architecture

```
ai/
├── core/
│   ├── config.py         # Pydantic AISettings (environment & default values)
│   └── logging.py        # AI module logging configuration
├── camera/
│   ├── source.py         # BaseCameraSource, WebcamSource, and VideoFileSource
│   └── frame_processor.py# Frame validation, metadata extraction, and FPS tracking
├── pipeline/
│   └── runner.py         # CameraPipelineRunner with GUI overlay & headless mode
└── tests/                # Automated unit & pipeline test suite
```

---

## ⚙️ Configuration Options

Configuration is managed via Pydantic `BaseSettings` (`ai/core/config.py`). Values can be overridden via environment variables or `.env` files prefixed with `AI_`.

| Variable | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `AI_SOURCE_TYPE` | `str` | `"WEBCAM"` | Input source (`WEBCAM` or `VIDEO_FILE`). |
| `AI_CAMERA_INDEX` | `int` | `0` | Device index for local/USB webcams (e.g. 0, 1). |
| `AI_VIDEO_PATH` | `str` | `None` | Path to local MP4/AVI file for `VIDEO_FILE` mode. |
| `AI_FRAME_WIDTH` | `int` | `None` | Optional target width for frame resizing. |
| `AI_FRAME_HEIGHT` | `int` | `None` | Optional target height for frame resizing. |
| `AI_DISPLAY_PREVIEW` | `bool` | `True` | Enable live OpenCV GUI window with overlays. |
| `AI_LOG_LEVEL` | `str` | `"INFO"` | Log verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`). |

---

## 🚀 Running the Camera Pipeline

### 1. Running with Local/USB Webcam
```bash
# Ensure virtualenv is active
python -m ai.pipeline.runner --source webcam --index 0
```
- Press **Q** or **ESC** while focusing the video preview window to cleanly release camera handles and exit.

### 2. Running with Local Video File (Fallback Mode)
```bash
python -m ai.pipeline.runner --source video_file --path data/test_videos/sample.mp4
```
- Reaches End-Of-File (EOF) and exits automatically without looping indefinitely.

### 3. Running in Headless Server / CI Mode (`DISPLAY_PREVIEW=false`)
```bash
python -m ai.pipeline.runner --source video_file --path data/test_videos/sample.mp4 --headless
```
- Bypasses all OpenCV GUI calls (`cv2.imshow`, `cv2.waitKey`), enabling seamless execution in server containers and CI pipelines.

---

## 🧪 Running AI Module Tests

```bash
# Run AI unit and pipeline tests (25 tests)
backend/.venv/bin/pytest ai/tests/ -v

# Run full project regression suite (123 tests: 98 M1 + 25 M2.1)
backend/.venv/bin/pytest backend/tests/ ai/tests/ -v
```

---

## 📊 Performance Benchmarking

To measure frame ingestion and processing throughput:

```bash
PYTHONPATH=. backend/.venv/bin/python ai/benchmarks/performance/benchmark_pipeline.py
```
- Automatically generates a 300-frame 1280x720 test stream and measures processing FPS and elapsed time.

---

## 🛠️ Troubleshooting & Hardware Notes

1. **Webcam Device Index**:
   - If index `0` fails to open on laptops with multiple video devices (e.g., built-in FaceTime HD camera vs USB webcam), specify index `1`:
     ```bash
     python -m ai.pipeline.runner --source webcam --index 1
     ```
2. **Headless Execution**:
   - If running inside Docker or SSH sessions without an X11/Cocoa display server, always pass `--headless` or set `AI_DISPLAY_PREVIEW=false`.
