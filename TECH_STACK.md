# IBVAP — Technology Stack & Architectural Rationale
## SIH Internal Round MVP

---

## 1. Stack Overview

```
┌────────────────────────────────────────────────────────────────────────┐
│                        FRONTEND DASHBOARD                              │
│         Next.js 14 (App Router) + React 18 + TypeScript + Tailwind     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTP REST & WebSocket (ws://)
┌───────────────────────────────────▼────────────────────────────────────┐
│                           BACKEND SERVICE                              │
│         FastAPI + Uvicorn + SQLAlchemy ORM + Pydantic + Hashlib        │
└───────────────────┬────────────────────────────────┬───────────────────┘
                    │ PostgreSQL 16                  │ Internal Pipeline API
┌───────────────────▼───────────────┐  ┌─────────────▼───────────────────┐
│         DATABASE STORAGE          │  │           AI ENGINE             │
│   Events, Alerts, Evidence, Users │  │  OpenCV + YOLOv8 + ByteTrack +  │
│         & Zone Definitions        │  │     OpenCV PIP Polygon Engine   │
└───────────────────────────────────┘  └─────────────────────────────────┘
```

---

## 2. Layer-by-Layer Technology Selection & Rationale

### 2.1 AI & Computer Vision Stack

| Technology | Selection | Rationale / Tradeoff Analysis |
| :--- | :--- | :--- |
| **Language** | Python 3.11 | De facto standard for computer vision; native bindings for OpenCV, PyTorch, NumPy. High developer velocity for ML integration. |
| **Frame Ingestion** | OpenCV (`opencv-python`) | Provides high-performance, low-level camera frame reading from webcams, USB cameras, and video files. Cross-platform support. |
| **Object Detection** | Ultralytics YOLOv8 (v8n) | Lightweight, single-stage anchor-free detector delivering state-of-the-art accuracy/speed balance for real-time edge processing (> 30 FPS on standard CPUs). |
| **Multi-Object Tracking** | ByteTrack | Association algorithm that utilizes low-score detection boxes alongside high-score boxes, dramatically improving tracking continuity and reducing ID switches during partial occlusions. |
| **Spatial Engine** | OpenCV & NumPy | Enables robust, mathematical point-in-polygon (`cv2.pointPolygonTest`) spatial testing with negligible computational overhead (< 1ms per track) and zero extra dependencies. |

### 2.2 Backend Stack

| Technology | Selection | Rationale / Tradeoff Analysis |
| :--- | :--- | :--- |
| **Framework** | FastAPI | Asynchronous Python framework leveraging Starlette and Pydantic. Built-in OpenAPI documentation, native WebSocket support, and low overhead. |
| **ASGI Server** | Uvicorn | Production-ready, lightning-fast ASGI web server implementation using `uvloop` and `httptools`. |
| **Database** | PostgreSQL 16 | Enterprise-grade ACID-compliant relational database. Supports `JSONB` data type for flexible polygon coordinate definitions. |
| **ORM & Migrations** | SQLAlchemy 2.0 + Alembic | Industry standard for Python ORM with type hints, async support, and declarative schema migrations. |
| **Evidence Hashing** | Python `hashlib` (SHA-256) | Standard library cryptographic module; zero extra overhead, deterministic SHA-256 binary calculation. |

### 2.3 Frontend Stack

| Technology | Selection | Rationale / Tradeoff Analysis |
| :--- | :--- | :--- |
| **Framework** | Next.js 14 (App Router) | React framework providing hybrid server/client rendering, file-based routing, and seamless WebSocket integration. |
| **Language** | TypeScript | Prevents runtime bugs, enforces strict API response typing, and improves component refactoring reliability. |
| **Styling** | Tailwind CSS | Utility-first CSS framework allowing rapid assembly of dark-themed, high-density security operational dashboards. |
| **Overlays** | HTML5 Canvas API | High-performance hardware-accelerated 2D canvas overlay for rendering bounding boxes and virtual fence polygons over video streams. |

### 2.4 DevOps & Infrastructure

| Technology | Selection | Rationale / Tradeoff Analysis |
| :--- | :--- | :--- |
| **Containerization** | Docker Compose | Local container orchestration for PostgreSQL, ensuring identical database state across all 6 student development environments. |
| **VCS & Workflow** | Git / GitHub | Feature-branch development workflow enforcing code reviews and modular section ownership. |
