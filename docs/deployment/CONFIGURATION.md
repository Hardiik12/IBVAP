# IBVAP Configuration & Environment Variables Reference

| Variable | Scope | Default / Example | Purpose |
| :--- | :--- | :--- | :--- |
| `POSTGRES_DB` | Database | `ibvap` | PostgreSQL database name |
| `POSTGRES_USER` | Database | `postgres` | PostgreSQL master user |
| `POSTGRES_PASSWORD` | Database | `<secret>` | PostgreSQL password |
| `DATABASE_URL` | Backend | `postgresql+psycopg://...` | SQLAlchemy database connection string |
| `JWT_SECRET_KEY` | Backend | `<32-char-random>` | Secret key for signing HS256 JWT tokens |
| `JWT_ALGORITHM` | Backend | `HS256` | JWT cryptographic algorithm |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Backend | `30` | Access token lifespan in minutes |
| `CORS_ORIGINS` | Backend | `http://localhost:3000` | Allowed browser origins |
| `EVIDENCE_ROOT` | Backend | `/app/data/evidence` | Physical directory storing snapshot JPEGs |
| `AI_BACKEND_URL`| AI Engine | `http://localhost:8000` | URL of FastAPI backend service |
| `AI_USERNAME` | AI Engine | `operator_user` | Service account username for event posts |
| `AI_PASSWORD` | AI Engine | `<secret>` | Service account password |
| `AI_SOURCE_TYPE`| AI Engine | `WEBCAM` / `VIDEO_FILE` | Ingestion source type |
| `AI_VIDEO_PATH` | AI Engine | `data/videos/...` | Local video file path for video ingestion |
| `AI_MODEL_SHA256`| AI Engine | `""` | Optional model weights checksum check |
| `NEXT_PUBLIC_API_URL` | Frontend | `http://localhost:8000` | Backend REST API URL |
| `NEXT_PUBLIC_WS_URL` | Frontend | `ws://localhost:8000/...` | WebSocket live events URL |
