# System Architecture (Draft)

High-level architecture overview for IBVAP Internal-Round MVP.

## Dataflow Pipeline
Camera Source → Video Capture → YOLO Detection → ByteTrack Tracking → Virtual Fence → Intrusion Event → FastAPI Backend → PostgreSQL → WebSocket Alert → Next.js Dashboard → Evidence Capture → SHA-256 Verification.
