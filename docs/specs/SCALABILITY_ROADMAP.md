# IBVAP — Scalability & Production Architecture Roadmap

This document contrasts the current SIH MVP architecture against the enterprise production scaling strategy.

---

## 1. Current SIH MVP Architecture (Localhost / Single Node)

```text
[ Camera / RTSP / Video File ]
             ↓
    [ AI Inference Worker ]
 (YOLOv8 + ByteTrack + PIP)
             ↓ (HTTP POST + JWT)
    [ FastAPI Backend ]
             ↓
     ┌───────┴───────┐
     ▼               ▼
[ PostgreSQL ]  [ In-Memory WS Manager ]
     │               │
     ▼               ▼
[ Local Disk ]  [ Next.js Tactical UI ]
 (Evidence)
```

- **Inference:** Single-worker process processing live webcam or video stream at **198+ FPS**.
- **Ingestion:** FastAPI application handling REST routing, JWT authentication, and RBAC authorization.
- **Persistence:** Relational PostgreSQL storing users, cameras, zones, events, alerts, and audit logs.
- **Evidence Storage:** Local filesystem storage with server-authoritative SHA-256 binary validation.
- **Real-Time Feed:** In-process `WebSocketManager` broadcasting post-commit JSON events.

---

## 2. Enterprise Production Architecture (Multi-Camera / Distributed)

```text
[ Camera Sector A ] [ Camera Sector B ] [ Camera Sector N ]
        │                   │                   │
        ▼ (RTSP)            ▼ (RTSP)            ▼ (RTSP)
┌─────────────────────────────────────────────────────────┐
│              Kubernetes AI Worker Pool                  │
│       (GPU-Accelerated YOLOv8 + TensorRT Nodes)         │
└───────────────────────────┬─────────────────────────────┘
                            ▼
           ┌───────────────────────────────────┐
           │     Apache Kafka / Redis Streams   │ (Event Queue)
           └────────────────┬──────────────────┘
                            ▼
           ┌───────────────────────────────────┐
           │     FastAPI Ingestion Workers     │ (Load-Balanced)
           └────────────────┬──────────────────┘
                            │
       ┌────────────────────┼────────────────────┐
       ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐     ┌──────────────┐
│  PostgreSQL  │    │ S3 / MinIO   │     │ Redis Pub/Sub│
│   Cluster    │    │Object Storage│     │  WS Gateway  │
│ (Multi-AZ)   │    │  (Evidence)  │     │  (Socket.io) │
└──────────────┘    └──────────────┘     └───────┬──────┘
                                                 ▼
                                     ┌───────────────────────┐
                                     │  Next.js Edge Cluster │
                                     │   (Distributed UI)    │
                                     └───────────────────────┘
```

---

## 3. Production Enhancements Matrix

| Component | Current MVP State | Future Production State | Priority |
|---|---|---|---|
| **Transport Encryption** | Plain HTTP / WS on localhost | Full TLS 1.3 / HTTPS / WSS with automated Let's Encrypt certificates | **P1** |
| **Evidence Storage** | Local directory (`data/evidence`) | S3/MinIO Object Storage with WORM (Write Once Read Many) policy | **P1** |
| **Event Broker** | Direct HTTP POST from AI | Apache Kafka / Redis Streams buffer for multi-camera fault tolerance | **P2** |
| **WebSocket Scaling** | In-process Python memory manager | Redis Pub/Sub with distributed WebSocket Gateway cluster | **P2** |
| **AI Inference** | CPU / MPS single-threaded runner | GPU TensorRT distributed inference nodes with auto-scaling | **P2** |
