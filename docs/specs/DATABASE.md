# IBVAP — Database Schema & Data Strategy
## SIH Internal Round MVP

---

## 1. Entity Relationship Overview

```
 ┌─────────────┐       1:N       ┌─────────────┐
 │   users     ├─────────────────┤ audit_logs  │
 └──────┬──────┘                 └─────────────┘
        │ 1:N (acknowledged_by)
 ┌──────▼──────┐       1:N       ┌─────────────┐
 │   cameras   ├─────────────────┤    zones    │
 └──────┬──────┘                 └──────┬──────┘
        │ 1:N                           │ 1:N
        └────────────────┐              │
                         ▼              ▼
                       ┌───────────────────┐
                       │      events       │
                       └────────┬──────────┘
                                │ 1:1 / 1:N
                ┌───────────────┴───────────────┐
                ▼ (CASCADE)                     ▼ (RESTRICT)
       ┌───────────────────┐           ┌───────────────────┐
       │      alerts       │           │     evidence      │
       └───────────────────┘           └───────────────────┘
```

---

## 2. Table Schemas & Implemented DDL Definitions

**Implementation Status**: `IMPLEMENTED (Backend Phase 2)`  
**Migration Revision**: `phase2_database_models`  
**ORM Base**: `app.db.base.Base`

### 2.1 `users` Table
Stores system user accounts and roles for RBAC.

```sql
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('OPERATOR', 'ANALYST', 'ADMINISTRATOR', 'AUDITOR')),
    is_active BOOLEAN DEFAULT 'true' NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);
CREATE UNIQUE INDEX ix_users_username ON users (username);
CREATE UNIQUE INDEX ix_users_email ON users (email);
```

### 2.2 `cameras` Table
Stores camera feed configurations.

```sql
CREATE TABLE cameras (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    camera_identifier VARCHAR(50) UNIQUE NOT NULL,
    source_type VARCHAR(20) NOT NULL CHECK (source_type IN ('WEBCAM', 'VIDEO_FILE', 'RTSP')),
    source_url VARCHAR(255),
    location VARCHAR(100),
    is_active BOOLEAN DEFAULT 'true' NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);
CREATE UNIQUE INDEX ix_cameras_camera_identifier ON cameras (camera_identifier);
```

### 2.3 `zones` Table
Stores polygon boundary configurations for virtual fencing.

```sql
CREATE TABLE zones (
    id VARCHAR(36) PRIMARY KEY,
    camera_id VARCHAR(36) NOT NULL REFERENCES cameras(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    zone_type VARCHAR(20) NOT NULL CHECK (zone_type IN ('RESTRICTED', 'MONITORED')),
    polygon_coordinates JSON NOT NULL, -- Format: [[x1,y1], [x2,y2], ...] normalized (0.0-1.0)
    is_active BOOLEAN DEFAULT 'true' NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);
CREATE INDEX ix_zones_camera_id ON zones (camera_id);
```

### 2.4 `events` Table
Persists generated security events (e.g., INTRUSION).

```sql
CREATE TABLE events (
    id VARCHAR(36) PRIMARY KEY,
    event_identifier VARCHAR(50) UNIQUE NOT NULL,
    event_type VARCHAR(50) NOT NULL CHECK (event_type IN ('INTRUSION', 'EXIT', 'LOITERING', 'UNAUTHORIZED_VEHICLE')),
    camera_id VARCHAR(36) NOT NULL REFERENCES cameras(id),
    zone_id VARCHAR(36) REFERENCES zones(id),
    track_id INTEGER NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    status VARCHAR(20) NOT NULL CHECK (status IN ('NEW', 'PROCESSED', 'ARCHIVED')),
    bounding_box JSON,
    position JSON,
    event_metadata JSON,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);
CREATE UNIQUE INDEX ix_events_event_identifier ON events (event_identifier);
CREATE INDEX idx_events_camera_timestamp ON events(camera_id, timestamp);
```

### 2.5 `alerts` Table
Tracks alert status associated with security events.

```sql
CREATE TABLE alerts (
    id VARCHAR(36) PRIMARY KEY,
    event_id VARCHAR(36) NOT NULL UNIQUE REFERENCES events(id) ON DELETE CASCADE,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    status VARCHAR(20) NOT NULL CHECK (status IN ('ACTIVE', 'ACKNOWLEDGED', 'RESOLVED')),
    message VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    acknowledged_by VARCHAR(36) REFERENCES users(id)
);
CREATE UNIQUE INDEX ix_alerts_event_id ON alerts (event_id);
```

### 2.6 `evidence` Table
Stores file references and SHA-256 cryptographic hashes for evidence snapshots.

```sql
CREATE TABLE evidence (
    id VARCHAR(36) PRIMARY KEY,
    evidence_identifier VARCHAR(50) UNIQUE NOT NULL,
    event_id VARCHAR(36) NOT NULL REFERENCES events(id) ON DELETE RESTRICT,
    file_path VARCHAR(255) NOT NULL,
    sha256_hash VARCHAR(64), -- Nullable initially until generated (Phase 6)
    captured_at TIMESTAMP WITH TIME ZONE NOT NULL,
    evidence_metadata JSON,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);
CREATE UNIQUE INDEX ix_evidence_evidence_identifier ON evidence (evidence_identifier);
CREATE INDEX ix_evidence_sha256_hash ON evidence (sha256_hash);
```

### 2.7 `audit_logs` Table
Records audit trails for security-sensitive actions.

```sql
CREATE TABLE audit_logs (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id VARCHAR(50),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    log_metadata JSON
);
CREATE INDEX ix_audit_logs_user_id ON audit_logs (user_id);
```

---

## 3. Data Storage & Efficiency Strategy

### Avoiding DB Explosion During Frame Processing
1. **Raw Frame Ingestion**: Raw video frames (30 FPS) are processed in memory and immediately discarded.
2. **Transient Detection Logs**: Frame-by-frame detections are held in RAM and passed to ByteTrack.
3. **Persisted Events Only**: Records are written to PostgreSQL **only when state transitions occur** (e.g., `OUTSIDE` → `INSIDE` triggering an `INTRUSION` event). This reduces database write operations from 1,800 writes/minute per camera to only actionable incidents (e.g. 1-5 writes/event).
