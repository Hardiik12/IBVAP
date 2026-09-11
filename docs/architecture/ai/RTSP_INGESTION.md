# IBVAP — Resilient RTSP Camera Ingestion Architecture

## 1. Architectural Overview

Phase 2.2 introduces production-oriented **Real-Time Streaming Protocol (RTSP) IP Camera Ingestion** for IBVAP.

```
┌─────────────────────────────────────────────────────────┐
│              RTSPCameraSource (ai/camera/rtsp.py)       │
├─────────────────────────────────────────────────────────┤
│  [Background Grabber Thread]                            │
│     │ (cv2.VideoCapture)                                │
│     ▼                                                   │
│  [Single-Slot Atomic Frame Buffer]                      │
│     │ (Latest BGR uint8 np.ndarray)                     │
│     ▼                                                   │
│  [Stale Frame Watchdog & Bounded Exponential Backoff]   │
└────────────────────────────┬────────────────────────────┘
                             │ read_frame() [Non-blocking]
                             ▼
              [AI Processing Pipeline Runner]
```

---

## 2. Key Technical Design Principles

1. **Non-Blocking Inference:**
   The OpenCV frame grabber executes inside a dedicated background worker thread (`_capture_loop`), preventing the main AI inference loop from blocking on socket read operations.
2. **Latest Frame Priority:**
   The stream buffer stores strictly a single atomic frame slot (`_latest_frame`). Older unconsumed frames are discarded, maintaining sub-10ms latency for real-time surveillance.
3. **Stale Stream Watchdog:**
   Monitors inter-frame arrival timestamps (`stale_frame_timeout=3.0s`). If no fresh frames arrive within the threshold, state transitions to `STALE` and reconnect flow triggers.
4. **Bounded Exponential Backoff:**
   Connection dropouts trigger automatic reconnect with exponential backoff (initial=1.0s, max=30.0s) and random jitter to avoid connection thundering herds.
5. **Credential Security & Redaction:**
   All RTSP URLs embedded with cleartext credentials (`rtsp://user:pass@host`) are redacted via regex (`sanitize_rtsp_url`) before logging or emitting telemetry status.

---

## 3. Empirical Verification Status

### VERIFIED:
- Unified camera abstraction compatibility ([`ai/camera/base.py`](file:///Users/hardik/Downloads/IBVAP/ai/camera/base.py), [`ai/camera/source.py`](file:///Users/hardik/Downloads/IBVAP/ai/camera/source.py)).
- Automated unit test suite (`ai/tests/camera/test_rtsp.py`) covering state transitions, backoff calculation, single-slot buffering, thread safety, and credential redaction.
- Non-networked test mock doubles passing cleanly.
- Full backend + AI regression test suite passing.

### NOT VERIFIED:
- Physical RTSP camera hardware integration (requires external IP camera device on network).
- GPU-accelerated video decoding (e.g. NVIDIA NVDEC / Jetson DeepStream).
- High-scale multi-camera cluster performance.
