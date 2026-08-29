# IBVAP — Database Schema & Data Strategy
## SIH Internal Round MVP

---

## 1. Entity Relationship Overview

```
 ┌─────────────┐       1:N       ┌─────────────┐
 │   users     ├─────────────────┤ audit_logs  │
 └─────────────┘                 └─────────────┘
        
 ┌─────────────┐       1:N       ┌─────────────┐
 │   cameras   ├─────────────────┤    zones    │
 └──────┬──────┘                 └──────┬──────┘
        │ 1:N                           │ 1:N
        └────────────────┐              │
                         ▼              ▼
                       ┌───────────────────┐
                       │      events       │
                       └────────┬──────────┘
                                │ 1:1
                ┌───────────────┴───────────────┐
                ▼                               ▼
       ┌───────────────────┐           ┌───────────────────┐
       │      alerts       │           │     evidence      │
       └───────────────────┘           └───────────────────┘
```

---

## 2. Table Schemas & DDL Definitions

### 2.1 `users` Table
Stores system user accounts and roles for RBAC.

```sql
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('OPERATOR', 'ANALYST', 'ADMIN', 'AUDITOR')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### 2.2 `cameras` Table
Stores camera feed configurations.

```sql
CREATE TABLE cameras (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    source_type VARCHAR(20) NOT NULL CHECK (source_type IN ('webcam', 'file', 'rtsp')),
    source_uri VARCHAR(255) NOT NULL,
    status VARCHAR(20) DEFAULT 'ACTIVE',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### 2.3 `zones` Table
Stores polygon boundary configurations for virtual fencing.

```sql
CREATE TABLE zones (
    id VARCHAR(36) PRIMARY KEY,
    camera_id VARCHAR(36) NOT NULL REFERENCES cameras(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    polygon_coordinates JSONB NOT NULL, -- Format: [[x1,y1], [x2,y2], ...] normalized (0.0-1.0)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### 2.4 `events` Table
Persists generated security events (e.g., INTRUSION).

```sql
CREATE TABLE events (
    id VARCHAR(36) PRIMARY KEY,
    camera_id VARCHAR(36) NOT NULL REFERENCES cameras(id),
    zone_id VARCHAR(36) REFERENCES zones(id),
    track_id INTEGER NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    class_name VARCHAR(50) NOT NULL,
    confidence FLOAT NOT NULL,
    bbox JSONB NOT NULL, -- Format: [x1, y1, x2, y2]
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_events_camera_timestamp ON events(camera_id, timestamp DESC);
```

### 2.5 `alerts` Table
Tracks alert status associated with security events.

```sql
CREATE TABLE alerts (
    id VARCHAR(36) PRIMARY KEY,
    event_id VARCHAR(36) NOT NULL UNIQUE REFERENCES events(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'UNACKNOWLEDGED' CHECK (status IN ('UNACKNOWLEDGED', 'ACKNOWLEDGED', 'DISMISSED')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### 2.6 `evidence` Table
Stores file references and SHA-256 cryptographic hashes for evidence snapshots.

```sql
CREATE TABLE evidence (
    id VARCHAR(36) PRIMARY KEY,
    event_id VARCHAR(36) NOT NULL UNIQUE REFERENCES events(id) ON DELETE CASCADE,
    file_path VARCHAR(255) NOT NULL,
    sha256_hash CHAR(64) NOT NULL,
    captured_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_evidence_sha256 ON evidence(sha256_hash);
```

### 2.7 `audit_logs` Table
Records audit trails for security-sensitive actions.

```sql
CREATE TABLE audit_logs (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    details JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

---

## 3. Data Storage & Efficiency Strategy

### Avoiding DB Explosion During Frame Processing
1. **Raw Frame Ingestion**: Raw video frames (30 FPS) are processed in memory and immediately discarded.
2. **Transient Detection Logs**: Frame-by-frame detections are held in RAM and passed to ByteTrack.
3. **Persisted Events Only**: Records are written to PostgreSQL **only when state transitions occur** (e.g., `OUTSIDE` → `INSIDE` triggering an `INTRUSION` event). This reduces database write operations from 1,800 writes/minute per camera to only actionable incidents (e.g. 1-5 writes/event).
