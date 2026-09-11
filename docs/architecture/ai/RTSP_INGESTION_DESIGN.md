# IBVAP — Phase 2.1 RTSP Stream Ingestion Design Specification

**Document Version:** 1.0.0 — Design & Architecture  
**Date:** 2026-09-11  
**Status:** 🟢 Architecture Specification  
**Target Milestone:** Phase 2.2 RTSP Physical CCTV Ingestion Implementation  
**Applicability:** `ai/camera/`, `ai/pipeline/`, `ai/core/`

---

## 1. Executive Summary & Design Goals

The Intelligent Border Video Analytics Platform (IBVAP) is expanding from local video files and USB webcams into physical IP surveillance networks via the **Real-Time Streaming Protocol (RTSP)**.

Border surveillance CCTV cameras (e.g., Hikvision, Dahua, Axis, Hanwha, Uniview, and ONVIF-compliant IP nodes) transmit H.264/H.265 video streams over IP networks that experience packet loss, Wi-Fi jitter, optical switch resets, and variable latency.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                RTSP DESIGN GOALS                                       │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. Zero Pipeline Blocking  │ Camera disconnects/freezes NEVER stall the AI pipeline.   │
│ 2. Sub-100ms Stream Latency│ Buffer size fixed at 1 frame; stale frames are purged.    │
│ 3. Automatic Reconnection  │ Exponential backoff with jitter on network drops.         │
│ 4. Credential Sanitization │ Passwords NEVER logged or exposed in exceptions/traces.   │
│ 5. 100% Backward Compat.   │ Zero breaking changes to Webcam, VideoFile, or Synthetic. │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Ingestion Architecture: Decoupled Threading Model

### The Problem with Naive OpenCV Ingestion
In a single-threaded architecture, calling `cv2.VideoCapture.read()` directly on the inference loop blocks the main thread for 30–60 seconds if an RTSP TCP socket hangs. Furthermore, internal OS/FFmpeg socket buffers accumulate frames while YOLO runs, leading to an ever-increasing latency lag (analyzing reality from 15 seconds ago).

### The IBVAP Decoupled Solution
IBVAP employs a **Producer-Consumer Threaded Architecture**:

```mermaid
flowchart TD
    subgraph Network ["Border IP Network"]
        Cam["Physical CCTV / RTSP Server (H.264/H.265)"]
    end

    subgraph RTSPSource ["RTSPCameraSource Component (ai/camera/rtsp.py)"]
        subgraph GrabberThread ["Background Grabber Thread (Producer)"]
            Worker["_capture_loop()"]
            Watchdog["Stream Watchdog (stale timeout > 3.0s)"]
            Backoff["Exponential Reconnect Engine"]
        end

        subgraph Buffer ["Lockless Single-Slot Buffer (Latest Frame)"]
            Slot["atomic_frame_slot [numpy.ndarray (H,W,3)]"]
            Meta["_last_frame_timestamp: float"]
        end
    end

    subgraph Consumer ["Main Inference Thread (ai/pipeline/runner.py)"]
        AIPipeline["AIPipeline.process_frame()"]
        YOLO["YOLOv8n + ByteTrack"]
        Zone["Polygon Zone Engine"]
    end

    Cam -->|RTSP TCP / RTP| Worker
    Worker -->|Write newest frame / drop stale| Slot
    Watchdog -->|Trigger reconnect if stalled| Backoff
    Backoff -->|Re-instantiate VideoCapture| Worker
    Slot -->|Non-blocking read() <= 1ms| AIPipeline
    AIPipeline --> YOLO --> Zone
```

1. **Background Grabber Thread (Producer):**
   - Continuously calls `cap.grab()` and `cap.retrieve()` at wire-speed.
   - Overwrites a thread-safe, single-slot atomic frame buffer.
   - If OpenCV buffers multiple packets, older frames are immediately dropped so the consumer always accesses the **latest real-time frame**.
2. **Foreground AI Pipeline (Consumer):**
   - Calls `read_frame()` / `read()` which returns immediately from the atomic slot in $\le 1	ext{ ms}$.
   - Never blocks on network I/O.
   - If the camera is offline/reconnecting, returns `(False, None)` or the last cached frame with a `STALE` status flag.

---

## 3. Video Backend Technology Evaluation & Selection

We evaluated three decoding technologies specifically for IBVAP edge surveillance workloads:

| Dimension | Option A: OpenCV VideoCapture (FFmpeg Backend) | Option B: Native PyAV / FFmpeg Subprocess | Option C: GStreamer / DeepStream |
| :--- | :--- | :--- | :--- |
| **CPU Utilization** | Moderate (Hardware-accelerated when configured) | Low-to-Moderate (Direct libav bindings) | Ultra-Low (NVDEC hardware decoders) |
| **Latency Control** | Excellent (via `CAP_PROP_BUFFERSIZE=1` & grab loops) | Excellent (Direct packet parsing) | Superior (Zero-copy pipelines) |
| **Reconnect Capability** | Simple & Reliable (Clean object re-instantiation) | High Complexity (Manual demux error recovery) | High Complexity (GstBus message handling) |
| **Codec Support** | H.264, H.265 (HEVC), MJPEG, MPEG4 | H.264, H.265, AV1, Proprietary CCTV | H.264, H.265, Jetson NVMM |
| **Deployment Footprint** | Standard PyPI (`opencv-python-headless`) | Requires `av` / compilation against `libavcodec` | Heavy OS packages (`libgstreamer1.0-dev`) |
| **Linux Edge / Jetson** | Compatible across all Linux, macOS, JetPack | Compatible, requires wheel builds | Native to Jetson DeepStream, complex on x86 |
| **Multi-Cam Scalability** | 8–16 cameras per edge node | 12–20 cameras per edge node | 24+ cameras (Jetson hardware decode) |

### **Architecture Decision: Option A (OpenCV with FFmpeg TCP Options)**
* **Rationale:** OpenCV is already fully integrated and tested across the 187-test suite. Standard `opencv-python-headless` dynamically links to FFmpeg.
* **Tuning Parameters:**
  ```python
  # Set environment flags before VideoCapture instantiation
  os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp|stimeout;5000000|buffer_size;1024000"
  ```
  - `rtsp_transport;tcp`: Enforces TCP interleaved streaming (eliminates UDP packet loss and artifact corruption over wireless/border links).
  - `stimeout;5000000`: Sets socket I/O timeout to 5.0 seconds (prevents indefinite C-level socket hang).
  - `buffer_size;1024000`: Minimal TCP socket receive buffer.

---

## 4. Class Design & Data Contract

`RTSPCameraSource` adheres to both `CameraSource` (`ai/camera/base.py`) and `BaseCameraSource` (`ai/camera/source.py`), ensuring complete drop-in compatibility.

```python
class CameraState(str, Enum):
    DISCONNECTED = "DISCONNECTED"
    CONNECTING = "CONNECTING"
    STREAMING = "STREAMING"
    STALE = "STALE"
    RECONNECTING = "RECONNECTING"
    ERROR = "ERROR"

class RTSPCameraSource(CameraSource, BaseCameraSource):
    """
    Resilient, non-blocking RTSP stream ingestion source with background frame
    grabbing, automatic exponential backoff reconnect, and credential sanitization.
    """
    def __init__(
        self,
        rtsp_url: str,
        camera_id: str = "cam-rtsp-01",
        name: str = "Border RTSP CCTV",
        reconnect_interval_base: float = 1.0,
        reconnect_interval_max: float = 30.0,
        stale_frame_timeout: float = 3.0,
        tcp_transport: bool = True,
        target_width: Optional[int] = None,
        target_height: Optional[int] = None,
    ) -> None: ...
```

### Core Interface Methods

| Method | Return Type | Behavior |
| :--- | :--- | :--- |
| `open()` | `bool` / `None` | Starts background grabber thread, begins initial RTSP handshake. |
| `read_frame()` | `tuple[bool, Optional[np.ndarray]]` | Instantaneous, non-blocking fetch from atomic slot. |
| `read()` | `tuple[bool, Optional[np.ndarray]]` | Alias for `read_frame()` (BaseCameraSource compatibility). |
| `is_opened()` | `bool` | Returns `True` if grabber thread is running and state is `STREAMING`. |
| `release()` | `None` | Signals grabber thread shutdown, drains sockets, releases `cv2.VideoCapture`. |
| `health_status()` | `dict` | Returns diagnostics (state, FPS, dropped frames, reconnect attempts, sanitized URL). |
| `@property resolution` | `tuple[int, int]` | Current stream resolution `(width, height)`. |
| `@property fps` | `float` | Ingestion stream frame rate. |

---

## 5. Security & Credential Redaction Specification

RTSP URLs typically contain embedded Basic/Digest credentials:
`rtsp://admin:BorderSecret2026@192.168.1.100:554/Streaming/Channels/101`

### Mandatory Redaction Rules:
1. **Never Log Plaintext URLs:** All loggers, exceptions, and audit records must pass URLs through `sanitize_rtsp_url()`.
2. **Redaction Pattern:**
   ```python
   def sanitize_rtsp_url(url: str) -> str:
       """Replaces password with '***' while preserving protocol, user, host, and path."""
       if not url:
           return ""
       # Regex replaces ://username:password@ with ://username:***@
       return re.sub(r"://([^:]+):([^@]+)@", r"://:***@", url)
   ```
3. **Database & API Security:**
   - In PostgreSQL `cameras.source_url`, store the complete URL needed for backend/AI connectivity.
   - When returning camera objects via `GET /api/v1/cameras`, sanitize the `source_url` field unless requested by an authenticated `ADMINISTRATOR` for configuration purposes.

---

## 6. Resiliency, Watchdog & Reconnection Engine

```mermaid
stateDiagram-v2
    [*] --> DISCONNECTED
    DISCONNECTED --> CONNECTING : open() called
    CONNECTING --> STREAMING : VideoCapture.isOpened() == True
    CONNECTING --> RECONNECTING : Connection failed (timeout/refused)
    
    STREAMING --> STALE : No new frame for > 3.0s
    STALE --> RECONNECTING : Trigger socket reset
    
    STREAMING --> RECONNECTING : cap.read() returned False
    RECONNECTING --> CONNECTING : Wait (T_backoff) seconds
    
    STREAMING --> DISCONNECTED : release() called
    RECONNECTING --> DISCONNECTED : release() called
    DISCONNECTED --> [*]
```

### Reconnect Formula with Jitter
To prevent "thundering herd" reconnection storms across 16 border cameras after a network switch restart:

19904T_{	ext{backoff}} = \min\left(T_{	ext{max}}, T_{	ext{base}} 	imes 2^{	ext{attempt}}ight) + 	ext{Uniform}(-0.5, 0.5)19904

- {	ext{base}} = 1.0	ext{ s}$
- {	ext{max}} = 30.0	ext{ s}$
- Jitter ensures distributed reconnection attempts over time.

---

## 7. Multi-Camera Process Scaling Model

For multi-camera border deployments (4–16 cameras per edge server):
- **Worker Process Isolation:** Each RTSP camera runs in a dedicated `multiprocessing.Process` executing `CameraPipelineRunner`.
- **Fault Isolation:** A network crash or memory leak on Camera #4 has zero impact on Camera #1, #2, or #3.
- **IPC Event Dispatch:** All workers dispatch events over HTTP REST to the unified FastAPI gateway.

---

## 8. Summary of Backward Compatibility

```
Existing Implementations              RTSP Extension
────────────────────────              ──────────────
ai/camera/base.py           ───────►  No changes required (compatible)
ai/camera/file.py           ───────►  No changes required (compatible)
ai/camera/webcam.py         ───────►  No changes required (compatible)
ai/camera/synthetic.py      ───────►  No changes required (compatible)
ai/camera/source.py         ───────►  Add RTSP branch to create_camera_source()
ai/core/config.py           ───────►  Add RTSP_URL and RTSP_TRANSPORT settings
```
