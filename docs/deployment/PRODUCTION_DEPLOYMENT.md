# IBVAP Production Deployment & Hardening Guide

---

## 1. Production Architecture Guidelines

For production border deployment at scale:
1. **Reverse Proxy & TLS Termination:** Place Nginx or Traefik in front of FastAPI and Next.js with TLS 1.3 encryption.
2. **Database Hardening:**
   - Use managed PostgreSQL with automated daily WAL backups.
   - Run least-privilege database user permissions.
3. **Secret Management:**
   - Generate cryptographically strong random secrets:
     ```bash
     openssl rand -hex 32
     ```
   - Inject secrets via environment variables or secret managers (Vault / AWS Secrets Manager / GCP Secret Manager).
4. **Edge Hardware Execution:**
   - Compile YOLOv8 and ByteTrack to TensorRT FP16 engines on NVIDIA Jetson edge devices for ultra-low latency inference.
