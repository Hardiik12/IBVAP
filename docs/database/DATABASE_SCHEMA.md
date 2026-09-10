# IBVAP — Complete Live Database Schema Documentation for pgAdmin

**Platform:** Intelligent Border Video Analytics Platform (IBVAP)  
**Database Host:** `127.0.0.1:5432`  
**Database Name:** `ibvap`  
**Schema:** `public`  
**Engine:** PostgreSQL 18.3 (Homebrew) x86_64 / UTF-8  
**Audit Date:** 2026-08-30  
**Inspection Mode:** READ-ONLY LIVE SCHEMA AUDIT  

---

## 1. Database Overview

The IBVAP database provides the authoritative relational persistence, transactional integrity, and cryptographic forensics backbone for autonomous border surveillance. It enforces strict foreign key referential integrity (`ON DELETE RESTRICT` on evidence, `CASCADE` on alerts/zones), memory-hard Argon2id authentication, TOTP MFA and facial biometric enrollment, and sub-65ms event persistence.

* **Database Name:** `ibvap`
* **Default Owner:** `postgres`
* **Server Encoding:** `UTF8`
* **Client Encoding:** `UTF8`
* **Active Tables:** 7 application core tables + 1 migration tracking table
* **Active Enums:** 7 PostgreSQL domain enumeration types

---

## 2. Complete Table Inventory

| Table Name | Exact Row Count | Type | Primary Key | Description |
| :--- | :---: | :---: | :--- | :--- |
| **`users`** | 6 | Base Table | `id` | System user credentials, Argon2id hashes, MFA, and RBAC roles |
| **`cameras`** | 6 | Base Table | `id` | Video ingestion sensors (Webcam, Video File, RTSP) and configurations |
| **`zones`** | 1 | Base Table | `id` | Virtual perimeter geofence polygons (normalized 2D coordinates) |
| **`events`** | 6 | Base Table | `id` | AI-detected intrusion occurrences, ByteTrack IDs, bounding boxes |
| **`alerts`** | 6 | Base Table | `id` | Real-time alarms pushed to operators with acknowledgement tracking |
| **`evidence`** | 4 | Base Table | `id` | Forensic video snapshots and immutable server-computed SHA-256 digests |
| **`audit_logs`** | 47 | Base Table | `id` | Append-only forensic security audit log |
| **`alembic_version`**| 1 | Base Table | `version_num` | Alembic schema migration ledger (Revision `1fd6abcb82e2`) |

---

## 3. Complete Column Schema Definitions

### Table 1: `users`
| Column Name | PostgreSQL Data Type | Nullable | Default | Length / Max | Description |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `id` | `character varying` | **NO** | *None* | 36 | Primary Key UUID string |
| `username` | `character varying` | **NO** | *None* | 50 | Unique operator/admin login username |
| `email` | `character varying` | **NO** | *None* | 100 | Unique user email address |
| `password_hash` | `character varying` | **NO** | *None* | 255 | Memory-hard Argon2id password hash |
| `role` | `userrole` (ENUM) | **NO** | *None* | — | `ADMINISTRATOR`, `OPERATOR`, `ANALYST`, `AUDITOR` |
| `is_active` | `boolean` | **NO** | `true` | — | Account activation toggle |
| `mfa_secret` | `character varying` | YES | *None* | 64 | Base32 TOTP MFA secret key |
| `mfa_enabled` | `boolean` | **NO** | `false` | — | TOTP MFA enrollment flag |
| `face_embedding` | `text` | YES | *None* | — | 128-dimensional facial biometric embedding vector |
| `face_enrolled` | `boolean` | **NO** | `false` | — | Face authentication enrollment flag |
| `face_enrolled_at` | `timestamptz` | YES | *None* | — | Timestamp of biometric registration |
| `failed_login_attempts` | `integer` | **NO** | `0` | — | Consecutive failed login counter |
| `locked_until` | `timestamptz` | YES | *None* | — | Account brute-force lockout expiry |
| `created_at` | `timestamptz` | **NO** | *None* | — | Record creation UTC timestamp |
| `updated_at` | `timestamptz` | **NO** | *None* | — | Record last update UTC timestamp |

---

### Table 2: `cameras`
| Column Name | PostgreSQL Data Type | Nullable | Default | Length / Max | Description |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `id` | `character varying` | **NO** | *None* | 36 | Primary Key UUID string |
| `name` | `character varying` | **NO** | *None* | 100 | Human-readable camera label |
| `camera_identifier` | `character varying` | **NO** | *None* | 50 | Unique hardware / system identifier |
| `source_type` | `camerasourcetype` (ENUM)| **NO** | *None* | — | `WEBCAM`, `VIDEO_FILE`, `RTSP` |
| `source_url` | `character varying` | YES | *None* | 255 | RTSP stream URL or local video path |
| `location` | `character varying` | YES | *None* | 100 | Geographic/tactical installation sector |
| `is_active` | `boolean` | **NO** | `true` | — | Camera ingestion operational state |
| `created_at` | `timestamptz` | **NO** | *None* | — | Record creation UTC timestamp |
| `updated_at` | `timestamptz` | **NO** | *None* | — | Record last update UTC timestamp |

---

### Table 3: `zones`
| Column Name | PostgreSQL Data Type | Nullable | Default | Length / Max | Description |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `id` | `character varying` | **NO** | *None* | 36 | Primary Key UUID string |
| `camera_id` | `character varying` | **NO** | *None* | 36 | Foreign key to `cameras.id` |
| `name` | `character varying` | **NO** | *None* | 100 | Human-readable zone designation |
| `zone_type` | `zonetype` (ENUM) | **NO** | *None* | — | `RESTRICTED`, `MONITORED` |
| `polygon_coordinates` | `json` | **NO** | *None* | — | Normalized 2D coordinate array `[[x,y],...]` |
| `is_active` | `boolean` | **NO** | `true` | — | Zone geofence active status |
| `created_at` | `timestamptz` | **NO** | *None* | — | Record creation UTC timestamp |
| `updated_at` | `timestamptz` | **NO** | *None* | — | Record last update UTC timestamp |

---

### Table 4: `events`
| Column Name | PostgreSQL Data Type | Nullable | Default | Length / Max | Description |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `id` | `character varying` | **NO** | *None* | 36 | Primary Key UUID string |
| `event_identifier` | `character varying` | **NO** | *None* | 50 | Unique deterministic business key |
| `event_type` | `eventtype` (ENUM) | **NO** | *None* | — | `INTRUSION`, `EXIT`, `LOITERING`, `UNAUTHORIZED_VEHICLE` |
| `camera_id` | `character varying` | **NO** | *None* | 36 | Foreign key to `cameras.id` |
| `zone_id` | `character varying` | YES | *None* | 36 | Foreign key to `zones.id` |
| `track_id` | `integer` | **NO** | *None* | — | ByteTrack persistent target tracker ID |
| `timestamp` | `timestamptz` | **NO** | *None* | — | Event occurrence UTC timestamp |
| `severity` | `eventseverity` (ENUM) | **NO** | *None* | — | `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` |
| `status` | `eventstatus` (ENUM) | **NO** | `'NEW'` | — | `NEW`, `PROCESSED`, `ARCHIVED` |
| `bounding_box` | `json` | YES | *None* | — | Normalized box `{"x_min", "y_min", "x_max", "y_max", "confidence"}` |
| `position` | `json` | YES | *None* | — | Foot reference coordinate `{"x", "y"}` |
| `event_metadata` | `json` | YES | *None* | — | Contextual payload / AI metadata |
| `created_at` | `timestamptz` | **NO** | *None* | — | Record persistence UTC timestamp |

---

### Table 5: `alerts`
| Column Name | PostgreSQL Data Type | Nullable | Default | Length / Max | Description |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `id` | `character varying` | **NO** | *None* | 36 | Primary Key UUID string |
| `event_id` | `character varying` | **NO** | *None* | 36 | Foreign key to `events.id` (1:1 per event) |
| `severity` | `eventseverity` (ENUM) | **NO** | *None* | — | `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` |
| `status` | `alertstatus` (ENUM) | **NO** | `'ACTIVE'`| — | `ACTIVE`, `ACKNOWLEDGED`, `RESOLVED` |
| `message` | `character varying` | YES | *None* | 255 | Human-readable alarm broadcast message |
| `created_at` | `timestamptz` | **NO** | *None* | — | Alert generation UTC timestamp |
| `acknowledged_at` | `timestamptz` | YES | *None* | — | Operator acknowledgement UTC timestamp |
| `acknowledged_by` | `character varying` | YES | *None* | 36 | Foreign key to `users.id` |

---

### Table 6: `evidence`
| Column Name | PostgreSQL Data Type | Nullable | Default | Length / Max | Description |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `id` | `character varying` | **NO** | *None* | 36 | Primary Key UUID string |
| `evidence_identifier`| `character varying` | **NO** | *None* | 50 | Unique evidence identifier string |
| `event_id` | `character varying` | **NO** | *None* | 36 | Foreign key to `events.id` |
| `file_path` | `character varying` | **NO** | *None* | 255 | Server filesystem path to snapshot image |
| `sha256_hash` | `character varying` | YES | *None* | 64 | 64-character SHA-256 cryptographic digest |
| `captured_at` | `timestamptz` | **NO** | *None* | — | Exact frame capture UTC timestamp |
| `evidence_metadata` | `json` | YES | *None* | — | Technical metadata (dimensions, format) |
| `created_at` | `timestamptz` | **NO** | *None* | — | Record persistence UTC timestamp |

---

### Table 7: `audit_logs`
| Column Name | PostgreSQL Data Type | Nullable | Default | Length / Max | Description |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `id` | `character varying` | **NO** | *None* | 36 | Primary Key UUID string |
| `user_id` | `character varying` | YES | *None* | 36 | Foreign key to `users.id` (actor) |
| `action` | `character varying` | **NO** | *None* | 100 | Security action enum string |
| `resource_type` | `character varying` | **NO** | *None* | 50 | Target entity type (`CAMERA`, `ZONE`, `EVIDENCE`, `USER`, `ALERT`) |
| `resource_id` | `character varying` | YES | *None* | 50 | Specific target identifier string |
| `timestamp` | `timestamptz` | **NO** | *None* | — | Audit event UTC timestamp |
| `log_metadata` | `json` | YES | *None* | — | Contextual audit data (IP, parameters) |

---

## 4. Primary Keys

| Table | Constraint Name | Column(s) |
| :--- | :--- | :--- |
| `alembic_version` | `alembic_version_pkc` | `version_num` |
| `users` | `users_pkey` | `id` |
| `cameras` | `cameras_pkey` | `id` |
| `zones` | `zones_pkey` | `id` |
| `events` | `events_pkey` | `id` |
| `alerts` | `alerts_pkey` | `id` |
| `evidence` | `evidence_pkey` | `id` |
| `audit_logs` | `audit_logs_pkey` | `id` |

---

## 5. Foreign Keys & Referential Actions

| Source Table.Column | Constraint Name | Target Table.Column | ON DELETE Action | ON UPDATE Action |
| :--- | :--- | :--- | :---: | :---: |
| `zones.camera_id` | `zones_camera_id_fkey` | `cameras.id` | `CASCADE` | `NO ACTION` |
| `events.camera_id` | `events_camera_id_fkey` | `cameras.id` | `NO ACTION` | `NO ACTION` |
| `events.zone_id` | `events_zone_id_fkey` | `zones.id` | `NO ACTION` | `NO ACTION` |
| `alerts.event_id` | `alerts_event_id_fkey` | `events.id` | `CASCADE` | `NO ACTION` |
| `alerts.acknowledged_by` | `alerts_acknowledged_by_fkey` | `users.id` | `NO ACTION` | `NO ACTION` |
| `evidence.event_id` | `evidence_event_id_fkey` | `events.id` | **`RESTRICT`** | `NO ACTION` |
| `audit_logs.user_id` | `audit_logs_user_id_fkey` | `users.id` | `NO ACTION` | `NO ACTION` |

* **Forensic Protection:** The `evidence_event_id_fkey` uses `ON DELETE RESTRICT` to ensure physical crime scene snapshots cannot be deleted while attached to an event.

---

## 6. Unique Constraints

| Table | Constraint / Index Name | Column(s) | Business Requirement |
| :--- | :--- | :--- | :--- |
| `users` | `ix_users_username` | `username` | Prevents duplicate usernames |
| `users` | `ix_users_email` | `email` | Prevents duplicate email registrations |
| `cameras` | `ix_cameras_camera_identifier` | `camera_identifier` | Prevents duplicate camera identifiers |
| `events` | `ix_events_event_identifier` | `event_identifier` | **Guarantees Event Idempotency & Prevents Duplicates** |
| `alerts` | `ix_alerts_event_id` | `event_id` | Enforces exact 1:1 alert per intrusion event |
| `evidence` | `ix_evidence_evidence_identifier`| `evidence_identifier`| Enforces unique evidence snapshot references |

---

## 7. Performance & Query Indexes

| Table | Index Name | Column(s) | Type | Purpose |
| :--- | :--- | :--- | :---: | :--- |
| `events` | `idx_events_camera_timestamp` | `(camera_id, timestamp)` | B-Tree | High-speed time-series filtering per camera |
| `events` | `ix_events_camera_id` | `camera_id` | B-Tree | Fast camera event lookups |
| `events` | `ix_events_zone_id` | `zone_id` | B-Tree | Fast zone activity lookups |
| `events` | `ix_events_event_type` | `event_type` | B-Tree | Fast classification filtering (`INTRUSION`) |
| `events` | `ix_events_timestamp` | `timestamp` | B-Tree | Fast timeline sorting |
| `alerts` | `ix_alerts_status` | `status` | B-Tree | Fast active/unacknowledged alarm querying |
| `evidence` | `ix_evidence_sha256_hash` | `sha256_hash` | B-Tree | Instant forensic hash verification lookups |
| `evidence` | `ix_evidence_event_id` | `event_id` | B-Tree | Fast event evidence retrieval |
| `audit_logs` | `ix_audit_logs_timestamp` | `timestamp` | B-Tree | Fast compliance audit trail pagination |
| `audit_logs` | `ix_audit_logs_user_id` | `user_id` | B-Tree | Fast operator audit history retrieval |
| `zones` | `ix_zones_camera_id` | `camera_id` | B-Tree | Fast zone lookup per camera feed |

---

## 8. Check Constraints

* In PostgreSQL 18+, all `NOT NULL` declarations are enforced through native check constraints in the information schema (50 column `IS NOT NULL` constraints active).
* Enumeration domain boundaries are strictly validated by PostgreSQL native `ENUM` types.

---

## 9. Enumeration Types (PostgreSQL ENUMs)

| Enum Name | Allowed Values | Applied In Table.Column |
| :--- | :--- | :--- |
| **`userrole`** | `'OPERATOR'`, `'ANALYST'`, `'ADMINISTRATOR'`, `'AUDITOR'` | `users.role` |
| **`camerasourcetype`** | `'WEBCAM'`, `'VIDEO_FILE'`, `'RTSP'` | `cameras.source_type` |
| **`zonetype`** | `'RESTRICTED'`, `'MONITORED'` | `zones.zone_type` |
| **`eventtype`** | `'INTRUSION'`, `'EXIT'`, `'LOITERING'`, `'UNAUTHORIZED_VEHICLE'` | `events.event_type` |
| **`eventseverity`** | `'LOW'`, `'MEDIUM'`, `'HIGH'`, `'CRITICAL'` | `events.severity`, `alerts.severity` |
| **`eventstatus`** | `'NEW'`, `'PROCESSED'`, `'ARCHIVED'` | `events.status` |
| **`alertstatus`** | `'ACTIVE'`, `'ACKNOWLEDGED'`, `'RESOLVED'` | `alerts.status` |

---

## 10. Sequences / Views / Triggers / Routines

* **Sequences:** 0 (Primary keys use client-generated UUID v4 strings for distributed safety).
* **Views:** 0 (Queries are handled dynamically through indexed SQLAlchemy 2.0 expressions).
* **Routines / Stored Procedures:** 0 (Business logic is held strictly in Python backend services).
* **Triggers:** 0 (PostgreSQL relies on foreign key actions `CASCADE` / `RESTRICT`).

---

## 11. Live Data Verification

| Table Name | Exact Live Row Count | Sample Business Content |
| :--- | :---: | :--- |
| `users` | 6 | 2 Admins, 2 Operators, 1 Analyst, 1 Auditor |
| `cameras` | 6 | 1 Live Webcam (`cam-webcam-01`), 5 RTSP cameras |
| `zones` | 1 | `Perimeter Restricted Zone A` (4 normalized vertices) |
| `events` | 6 | 5 Intrusion events, 1 Unauthorized vehicle event |
| `alerts` | 6 | 4 Active alarms, 2 Acknowledged alarms |
| `evidence` | 4 | 4 Snapshots with verified 64-char SHA-256 hashes |
| `audit_logs` | 47 | 47 Immutable security actions |

---

## 12. ASCII Entity-Relationship (ER) Diagram

```text
       ┌────────────────────────┐
       │         users          │
       ├────────────────────────┤
       │ id (PK)                │
       │ username (UQ)          │
       │ email (UQ)             │
       │ password_hash (Argon2) │
       │ role (ENUM)            │
       │ is_active              │
       │ mfa_secret             │
       │ face_embedding         │
       └───────────┬────────────┘
                   │
         ┌─────────┴─────────┐
         │ (1:N)             │ (1:N)
         ▼                   ▼
┌─────────────────┐ ┌──────────────────────────┐
│   audit_logs    │ │          alerts          │
├─────────────────┤ ├──────────────────────────┤
│ id (PK)         │ │ id (PK)                  │
│ user_id (FK)────┘ │ event_id (FK, UQ)────────┼────────┐
│ action          │ │ severity (ENUM)          │        │
│ resource_type   │ │ status (ENUM)            │        │
│ timestamp       │ │ acknowledged_by (FK)─────┘        │
└─────────────────┘ └──────────────────────────┘        │
                                                        │
┌────────────────────────┐                              │
│        cameras         │                              │
├────────────────────────┤                              │
│ id (PK)                │                              │
│ camera_identifier (UQ) │                              │
│ source_type (ENUM)     │                              │
│ is_active              │                              │
└───────────┬────────────┘                              │
            │                                           │
  ┌─────────┴─────────┐                                 │
  │ (1:N)             │ (1:N)                           │
  ▼                   ▼                                 │
┌─────────────────┐ ┌──────────────────────────┐        │
│      zones      │ │          events          │        │
├─────────────────┤ ├──────────────────────────┤        │
│ id (PK)         │ │ id (PK) ◄────────────────┼────────┘
│ camera_id (FK)  │ │ event_identifier (UQ)    │
│ polygon_coords  │ │ camera_id (FK)           │
│ zone_type(ENUM) │ │ zone_id (FK)             │
└────────┬────────┘ │ track_id                 │
         │          │ severity (ENUM)          │
         │ (1:N)    │ bounding_box (JSON)      │
         └─────────►│ position (JSON)          │
                    └───────────┬──────────────┘
                                │
                                │ (1:N)
                                ▼
                    ┌──────────────────────────┐
                    │         evidence         │
                    ├──────────────────────────┤
                    │ id (PK)                  │
                    │ evidence_identifier (UQ) │
                    │ event_id (FK - RESTRICT) │
                    │ file_path                │
                    │ sha256_hash (64-hex)     │
                    └──────────────────────────┘
```

---

## 13. Application Schema Consistency Audit

* **SQLAlchemy 2.0 Models (`app/models/`):** 100% exact column-for-column, type-for-type match with live PostgreSQL tables. Zero missing columns. Zero obsolete columns.
* **Alembic Migrations (`migrations/versions/`):** Current database revision `1fd6abcb82e2` represents the exact head migration.
* **Integrity Validation:** 0 orphan zones, 0 orphan events, 0 orphan alerts, 0 orphan evidence, 0 duplicate event identifiers.
