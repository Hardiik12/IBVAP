# IBVAP — System Requirements & Specifications
## SIH Internal Round MVP

---

## 1. Environment & Hardware Requirements

### 1.1 Development & Demo Hardware
- **Processor**: Intel Core i5/i7 (10th Gen+) or Apple Silicon (M1/M2/M3/M4) or AMD Ryzen 5/7.
- **Memory (RAM)**: Minimum 8 GB (16 GB recommended).
- **Storage**: 10 GB free disk space (SSD recommended).
- **Camera Device**: Integrated laptop webcam or standard USB webcam (720p @ 30 FPS minimum).

### 1.2 Host Operating System
- macOS 13+ / Linux (Ubuntu 22.04 LTS+) / Windows 11 with WSL2.

---

## 2. Software Stack & Runtime Dependencies

### 2.1 AI Engine Runtimes
- **Python Version**: Python 3.11.x
- **Core Python Libraries**:
  - `opencv-python>=4.9.0` (Video capture, frame manipulation, annotations)
  - `ultralytics>=8.1.0` (YOLOv8 object detection)
  - `numpy>=1.26.0` (Array operations, bounding box math)
  - `shapely>=2.0.0` (Polygon representation and point-in-polygon spatial testing)
  - `scipy>=1.12.0` & `lap>=0.4.0` (ByteTrack linear assignment algorithm)

### 2.2 Backend Service Runtimes
- **Framework**: `fastapi>=0.110.0`
- **ASGI Server**: `uvicorn[standard]>=0.28.0`
- **Database**: PostgreSQL 16.x (via Docker Compose container)
- **ORM & Migrations**: `sqlalchemy>=2.0.28`, `alembic>=1.13.1`, `psycopg[binary]>=3.1.18`
- **Authentication & Security**: `python-jose[cryptography]>=2.3.4`, `passlib[bcrypt]>=1.7.4`, `pydantic>=2.6.4`
- **HTTP & Testing**: `httpx>=0.27.0`, `pytest>=8.0.0`, `pytest-asyncio>=0.23.0`

### 2.3 Frontend Application Runtimes
- **Node.js**: Node.js 18.x LTS or 20.x LTS
- **Package Manager**: `npm` 10.x
- **Framework**: Next.js 14.x (App Router), React 18.x, TypeScript 5.x
- **Styling & UI**: Tailwind CSS 3.4.x, Lucide React (Icons), HTML5 Canvas API for stream overlays

---

## 3. Database System Requirements

- **PostgreSQL Database Server**: PostgreSQL 16.x
- **Database Name**: `ibvap`
- **Default Port**: `5432`
- **Persistence Volume**: Docker volume `postgres_data`

---

## 4. API & Protocol Specifications

- **HTTP API Base URL**: `http://localhost:8000/api/v1`
- **WebSocket Feed URL**: `ws://localhost:8000/ws/alerts`
- **Frontend App URL**: `http://localhost:3000`

---

## 5. Security & Verification Requirements

- **Hash Algorithm**: SHA-256 (via Python standard library `hashlib`).
- **Token Auth**: OAuth2 Bearer Tokens (JWT with HS256 algorithm).
- **Password Encryption**: bcrypt salt + hashing.
