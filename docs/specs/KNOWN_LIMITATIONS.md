# IBVAP — Known Limitations & MVP Constraints

This document transparently records the architectural boundaries of the current SIH Internal Round MVP and defines the roadmap for production enhancements.

---

## 1. MVP Limitations vs. Production Roadmap

| Area | Current MVP Implementation | Enterprise Production Roadmap | Classification |
|---|---|---|---|
| **Transport Layer** | HTTP/WS on localhost demo environment | Full HTTPS / WSS with TLS 1.3 certificates | **Production Roadmap** |
| **Evidence Storage** | Local structured filesystem directory (`data/evidence/`) | AWS S3 / MinIO Object Storage with Write-Once-Read-Many (WORM) | **Production Roadmap** |
| **WebSocket Broker** | In-process Python async manager (`WebSocketManager`) | Distributed Redis Pub/Sub cluster with sticky session gateway | **Scalability Roadmap** |
| **Rate Limiter State**| In-memory sliding window rate limiter | Distributed Redis token bucket limiter | **Scalability Roadmap** |
| **Video Ingestion** | Single-worker process processing live stream / file | Multi-worker Kubernetes cluster with TensorRT GPU acceleration | **Scalability Roadmap** |
| **Database Instance** | Single PostgreSQL instance with local connection pooling | Multi-AZ Primary-Replica cluster with automated failover | **Production Roadmap** |

---

## 2. Conclusion
None of the above limitations represent P0 defects for the SIH Internal Round demonstration. The MVP completely satisfies all functional, architectural, security, and verification requirements.
