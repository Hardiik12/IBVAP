# IBVAP AI / Computer Vision Module

AI, Detection, Tracking, and Virtual Fencing Engine for IBVAP.

## Section Lead
M2 — AI/ML Lead  
M3 — Video/Edge Lead  

## Components Overview
- `camera/`: Video stream capture and abstraction (webcam, file, RTSP).
- `detection/`: Object detector wrappers (Ultralytics YOLO).
- `tracking/`: Multi-object tracker integration (ByteTrack).
- `zones/`: Polygon geometry and point-in-polygon spatial evaluation.
- `events/`: Intrusion state transition and event decision engine.
- `pipeline/`: Frame processing orchestrator linking input to event output.

## Structure
```
ai/
├── camera/        # Frame ingestion and camera interfaces
├── detection/     # YOLO detector implementation & bounding box normalization
├── tracking/      # ByteTrack tracker for identity persistence
├── zones/         # Virtual fence polygon spatial engine
├── events/        # Event generation & state transition logic
├── pipeline/      # End-to-end stream processing pipeline
├── models/        # Model weights directory (gitignored)
├── benchmarks/    # Performance & accuracy evaluation scripts
└── tests/         # Unit tests for AI components
```

## Getting Started
```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```
