# IBVAP — System Architecture & Pipeline Design
## SIH Internal Round MVP

---

## 1. High-Level Architecture Overview

IBVAP follows a decoupled, three-tier modular architecture:
1. **AI Processing Engine** (Stream Ingestion, Object Detection, Tracking, Spatial Logic, Event Generation)
2. **Backend Application Server** (FastAPI Service Layer, PostgreSQL Storage, Real-Time WebSockets, SHA-256 Verification Engine)
3. **Frontend Operational Dashboard** (Next.js Single Page Application, Video/Overlay Player, Alert Feed, Evidence Verification Modal)

```
                       +-----------------------------+
                       |   Physical / File Camera    |
                       +--------------+--------------+
                                      |
                                  Raw Frame
                                      v
+--------------------------------------------------------------------------+
|                            AI ENGINE (Python)                            |
|  +----------------+    +----------------+    +------------------------+  |
|  | OpenCV Reader  | -> | YOLOv8 Detect  | -> |  ByteTrack Tracker     |  |
|  +----------------+    +----------------+    +-----------+------------+  |
|                                                          |               |
|                                                     Track State          |
|                                                          v               |
|  +----------------+    +----------------+    +------------------------+  |
|  | Event Dispatch | <- | Event Engine   | <- | Polygon Zone Engine    |  |
|  +-------+--------+    +----------------+    +------------------------+  |
+----------|---------------------------------------------------------------+
           |
      HTTP Event Payload
           v
+--------------------------------------------------------------------------+
|                          BACKEND SERVER (FastAPI)                        |
|  +----------------+    +----------------+    +------------------------+  |
|  | REST API Router|    | Service Layer  |    | WebSocket Broadcaster  |  |
|  +-------+--------+    +-------+--------+    +-----------+------------+  |
|          |                     |                         |               |
|          v                     v                         |               |
|  +----------------+    +----------------+                |               |
|  |  PostgreSQL DB |    | SHA-256 Engine |                |               |
|  +----------------+    +----------------+                |               |
+----------------------------------------------------------|---------------+
                                                           |
                                               WebSocket / REST Data
                                                           v
+--------------------------------------------------------------------------+
|                     FRONTEND DASHBOARD (Next.js)                         |
|  +----------------+    +----------------+    +------------------------+  |
|  | Live Monitor   |    | Real-Time Feed |    | Evidence Verification  |  |
|  | Canvas Overlay |    | Alerts Table   |    | Tamper Inspector Modal |  |
|  +----------------+    +----------------+    +------------------------+  |
+--------------------------------------------------------------------------+
```

---

## 2. AI Processing Pipeline Lifecycle

The AI engine executes a continuous frame processing loop:

```
[Frame Capture] 
       │ 1. Read BGR numpy array frame from CameraSource
       ▼
[Detector Inference] 
       │ 2. YOLOv8 predicts bounding boxes, class IDs, confidences
       ▼
[Data Normalization] 
       │ 3. Format into NormalizedDetections: [x1, y1, x2, y2, conf, class_id]
       ▼
[Tracker Association] 
       │ 4. ByteTrack matches detections to active tracks, assigns persistent track_id
       ▼
[Spatial Point Math] 
       │ 5. Compute bottom-center reference point: (x_center = (x1+x2)/2, y_bottom = y2)
       ▼
[Zone Containment Test] 
       │ 6. Shapely ray-casting PIP checks point against active zone polygon
       ▼
[State Machine Evaluation] 
       │ 7. Compare current zone state with previous track state:
       │    - OUTSIDE -> INSIDE: Trigger INTRUSION Event & state = INSIDE
       │    - INSIDE  -> INSIDE: Maintain state (Suppress duplicate event)
       │    - INSIDE  -> OUTSIDE: Reset state = OUTSIDE
       ▼
[Event & Evidence Dispatch] 
            - Save snapshot frame to data/evidence/<id>.jpg
            - Post event payload + snapshot metadata to Backend API
```

---

## 3. Data Normalization Contracts

To prevent model lock-in, the AI engine enforces strict internal dataclass representations:

### 3.1 Normalized Detection Dict
```json
{
  "class_id": 0,
  "class_name": "person",
  "confidence": 0.92,
  "bbox": [150.0, 220.0, 310.0, 590.0]
}
```

### 3.2 Track State Object
```json
{
  "track_id": 17,
  "class_name": "person",
  "confidence": 0.92,
  "bbox": [150.0, 220.0, 310.0, 590.0],
  "reference_point": [230.0, 590.0],
  "current_zone_state": "INSIDE",
  "last_updated": "2026-08-29T18:30:00.100Z"
}
```

---

## 4. Evidence Hashing & Verification Pipeline

```
                     INTRUSION EVENT DETECTED
                                │
                                ▼
                     Save Frame Snapshot (.jpg)
                                │
                                ▼
                  Read Binary Image File Bytes
                                │
                                ▼
                 Compute SHA-256 Hash Digest
                  (64-character Hexadecimal)
                                │
                                ▼
              Save Record in Database (file_path + hash)
                                │
    ┌───────────────────────────┴───────────────────────────┐
    ▼                                                       ▼
[Verification Test]                                [Tamper Demonstration]
    │                                                       │
Read File Bytes from Disk                               Edit File Bytes / Save Copy
    │                                                       │
Compute Current SHA-256                                 Compute Current SHA-256
    │                                                       │
Compare (Current == Stored)                             Compare (Current == Stored)
    │                                                       │
    ▼                                                       ▼
Result: VERIFIED (Match)                                Result: TAMPERED (Mismatch)
```

---

## 5. Architectural Principles

1. **Separation of AI and Business Domain**: YOLO and ByteTrack do not know about database schemas or REST endpoints. They emit pure event data structures.
2. **Stateless Service Handlers**: Backend service layer methods maintain idempotency and do not hold transient camera state.
3. **Optimized DB I/O**: Frame detections are processed entirely in-memory; only structured security events, alerts, and evidence metadata are persisted to PostgreSQL.
