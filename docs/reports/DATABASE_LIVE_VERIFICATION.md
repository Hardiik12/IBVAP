# IBVAP — Live PostgreSQL Database Structure & Data Verification Report

**Audit Mode:** READ-ONLY LIVE VERIFICATION  
**Database Host:** `127.0.0.1:5432`  
**Database Name:** `ibvap`  
**Schema:** `public`  
**PostgreSQL Version:** PostgreSQL 18.3 (Homebrew) on x86_64-apple-darwin23.6.0  
**Timestamp:** 2026-08-30  
**Status:** 🟢 **ALL CHECKS PASSED — 100% COMPLETE & CONSISTENT**  

---

## 1. Database Connectivity

| Check | Expected | Live Database State | Status |
| :--- | :--- | :--- | :---: |
| **Reachable** | True | `127.0.0.1:5432` accepting connections | 🟢 PASS |
| **Database Target** | `ibvap` | `current_database() = ibvap` | 🟢 PASS |
| **Active Schema** | `public` | `current_schema() = public` | 🟢 PASS |
| **Active User** | `postgres` | `current_user = postgres` | 🟢 PASS |
| **PostgreSQL Version** | 15+ | PostgreSQL 18.3 (Homebrew) x86_64 | 🟢 PASS |
| **Backend Configuration** | `DATABASE_URL` matches target | `postgresql+psycopg://postgres:***@localhost:5432/ibvap` | 🟢 PASS |

---

## 2. Core Tables & Row Counts

All **7 expected core tables** (plus the Alembic migration ledger) are present in the live database:

| Table Name | Row Count | Primary Key | Foreign Key References | Unique Indexes / Constraints | Status |
| :--- | :---: | :--- | :--- | :--- | :---: |
| **`users`** | 6 | `id` (VARCHAR) | None | `ix_users_username`, `ix_users_email` | 🟢 PASS |
| **`cameras`** | 6 | `id` (VARCHAR) | None | `ix_cameras_camera_identifier` | 🟢 PASS |
| **`zones`** | 1 | `id` (VARCHAR) | `camera_id` $\rightarrow$ `cameras.id` (CASCADE) | `zones_pkey` | 🟢 PASS |
| **`events`** | 6 | `id` (VARCHAR) | `camera_id` $\rightarrow$ `cameras.id`, `zone_id` $\rightarrow$ `zones.id` | `ix_events_event_identifier` | 🟢 PASS |
| **`alerts`** | 6 | `id` (VARCHAR) | `event_id` $\rightarrow$ `events.id` (CASCADE), `acknowledged_by` $\rightarrow$ `users.id` | `ix_alerts_event_id` (1:1 per event) | 🟢 PASS |
| **`evidence`** | 4 | `id` (VARCHAR) | `event_id` $\rightarrow$ `events.id` (RESTRICT) | `ix_evidence_evidence_identifier` | 🟢 PASS |
| **`audit_logs`** | 47 | `id` (VARCHAR) | `user_id` $\rightarrow$ `users.id` | `audit_logs_pkey` | 🟢 PASS |
| **`alembic_version`**| 1 | `version_num` | None | Head: `1fd6abcb82e2` | 🟢 PASS |

---

## 3. Users & RBAC Architecture

The live `users` table contains all 4 mandatory security roles:

| Role Enum | Live User Count | Argon2id Hash Present | MFA Fields (`mfa_secret`, `mfa_enabled`) | Face Biometrics Fields | Active State |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **`ADMINISTRATOR`** | 2 | 🟢 YES (`$argon2id$v=19$...`) | 🟢 Present | 🟢 Present | 🟢 Active |
| **`OPERATOR`** | 2 | 🟢 YES (`$argon2id$v=19$...`) | 🟢 Present | 🟢 Present | 🟢 Active |
| **`ANALYST`** | 1 | 🟢 YES (`$argon2id$v=19$...`) | 🟢 Present | 🟢 Present | 🟢 Active |
| **`AUDITOR`** | 1 | 🟢 YES (`$argon2id$v=19$...`) | 🟢 Present | 🟢 Present | 🟢 Active |

* **Argon2id Hash Present:** 🟢 **YES** (100% of accounts use memory-hard Argon2id hashes, zero plaintext passwords).
* **MFA/TOTP Columns:** 🟢 `mfa_secret` (VARCHAR), `mfa_enabled` (BOOLEAN).
* **Face Verification Columns:** 🟢 `face_embedding` (TEXT), `face_enrolled` (BOOLEAN), `face_enrolled_at` (TIMESTAMPTZ).
* **Account Lockout Columns:** 🟢 `failed_login_attempts` (INTEGER), `locked_until` (TIMESTAMPTZ).

---

## 4. Cameras Structure & Live Data

* **Live Cameras Registered:** 6 records (`cam-webcam-01`, test RTSP cameras).
* **Required Fields Present:** `id`, `name`, `camera_identifier`, `source_type`, `source_url`, `location`, `is_active`, `created_at`, `updated_at`.
* **Source Types Supported in Database:** `WEBCAM`, `VIDEO_FILE`, `RTSP` (mapped to PostgreSQL enum `camerasourcetype`).
* **Active Status:** 🟢 All cameras marked `is_active = TRUE`.

---

## 5. Virtual Polygon Zones

* **Live Zones Registered:** 1 active restricted perimeter zone (`Perimeter Restricted Zone A`).
* **Foreign Key Integrity:** 🟢 References camera `e4b2d35c-8dfa-4fb4-81d0-1e5b128dc90e` (`cam-webcam-01`).
* **Coordinate Data Integrity:** 
  - Stored as JSON array of 2D vertex pairs: `[[x1, y1], [x2, y2], [x3, y3], [x4, y4]]`.
  - Coordinate range check: $0.0 \le x, y \le 1.0$ (100% normalized to camera resolution).
* **Orphan Zones:** 🟢 **0** orphan zones.

---

## 6. Events Architecture & Idempotency

* **Live Events Logged:** 6 intrusion events.
* **Event Data Integrity:**
  - `event_type`: `INTRUSION`, `UNAUTHORIZED_VEHICLE` (mapped to PostgreSQL enum `eventtype`).
  - `severity`: `CRITICAL`, `HIGH` (mapped to PostgreSQL enum `eventseverity`).
  - `status`: `NEW`, `PROCESSED` (mapped to PostgreSQL enum `eventstatus`).
  - `track_id`: Integer ByteTrack identifiers (`1`, `4`, `42`, `77`, `999`).
  - `bounding_box`: Structured JSON with normalized coordinates (`x_min`, `y_min`, `x_max`, `y_max`, `confidence`).
  - `position`: Structured JSON foot-point reference coordinate (`(x_min+x_max)/2, y_max`).
* **Idempotency Protection:**
  - Unique constraint & index `ix_events_event_identifier` enforced on `event_identifier`.
  - Duplicate check: 🟢 **0 duplicate identifiers**.
* **Orphan Events:** 🟢 **0** orphan events.

---

## 7. Alerts & Acknowledgement Workflow

* **Live Alerts Logged:** 6 alert notifications.
* **Event Relationship:** 1:1 Foreign key mapping `alerts.event_id` $\rightarrow$ `events.id` (Cascade on delete).
* **Alert Statuses in Live DB:** `ACTIVE`, `ACKNOWLEDGED` (mapped to PostgreSQL enum `alertstatus`).
* **Operator Acknowledgement Fields:**
  - `acknowledged_by` (FK to `users.id`).
  - `acknowledged_at` (timezone-aware UTC timestamp).
* **Orphan Alerts:** 🟢 **0** orphan alerts.

---

## 8. Forensic Evidence & SHA-256 Integrity

* **Live Evidence Records:** 4 forensic snapshot records.
* **Event Relationship:** Foreign key `evidence.event_id` $\rightarrow$ `events.id` with `ON DELETE RESTRICT` (prevents evidence destruction).
* **SHA-256 Format Verification:**
  - Format check: `^[0-9a-fA-F]{64}$` (64-character hexadecimal digest).
  - Invalid hash count: 🟢 **0** invalid hashes.
* **Orphan Evidence:** 🟢 **0** orphan evidence records.

---

## 9. Immutable Audit Trail

* **Live Audit Log Records:** 47 immutable security events.
* **Recorded Action Enums:**
  - `LOGIN` & `LOGIN_FAILURE` (Authentication audits).
  - `CAMERA_CREATED`, `CAMERA_UPDATED` (Camera mutations).
  - `ZONE_CREATED` (Perimeter security changes).
  - `ALERT_ACKNOWLEDGED` (Operator triage actions).
  - `EVIDENCE_VERIFIED` (SHA-256 cryptographic verification checks).
  - `AUDIT_EXPORTED` (Compliance export events).
* **Timestamp & User Integrity:**
  - `timestamp`: Timezone-aware UTC with index `ix_audit_logs_timestamp`.
  - `user_id`: Foreign key reference to `users.id`.
* **Orphan Audit Records:** 🟢 **0** orphan records with invalid user IDs.

---

## 10. Database Integrity Matrix

| Integrity Check Description | Live Query Result | Status |
| :--- | :---: | :---: |
| **Orphan Cameras** | 0 | 🟢 PASS |
| **Orphan Zones** (non-existent camera) | 0 | 🟢 PASS |
| **Orphan Events** (non-existent camera or zone) | 0 | 🟢 PASS |
| **Orphan Alerts** (non-existent event) | 0 | 🟢 PASS |
| **Orphan Evidence** (non-existent event) | 0 | 🟢 PASS |
| **Orphan Audit Logs** (non-existent user ID) | 0 | 🟢 PASS |
| **Broken Foreign Keys** | 0 | 🟢 PASS |
| **NULL Values in Required Columns** | 0 | 🟢 PASS |
| **Duplicate `event_identifier` Records** | 0 | 🟢 PASS |
| **Invalid SHA-256 Hash Length / Format** | 0 | 🟢 PASS |
| **Invalid User Role Enums** | 0 | 🟢 PASS |
| **Invalid Alert Status Enums** | 0 | 🟢 PASS |

---

## 11. Indexes & Referential Protections

* **Primary Keys:** Enforced on all 7 core tables + `alembic_version`.
* **Unique Constraints:**
  - `ix_users_username` on `users(username)`
  - `ix_users_email` on `users(email)`
  - `ix_cameras_camera_identifier` on `cameras(camera_identifier)`
  - `ix_events_event_identifier` on `events(event_identifier)`
  - `ix_alerts_event_id` on `alerts(event_id)`
  - `ix_evidence_evidence_identifier` on `evidence(evidence_identifier)`
* **Performance Indexes:**
  - `idx_events_camera_timestamp` on `events(camera_id, timestamp)` (Fast temporal queries)
  - `ix_evidence_sha256_hash` on `evidence(sha256_hash)` (Fast hash lookups)
  - `ix_audit_logs_timestamp` on `audit_logs(timestamp)` (Fast audit filtering)
* **Deletion Constraints:**
  - `ON DELETE CASCADE` for ephemeral alerts and camera zones.
  - `ON DELETE RESTRICT` on `evidence.event_id` to prevent deletion of forensic records.

---

## 12. Schema $\leftrightarrow$ Code Consistency (SQLAlchemy / Alembic)

Comparing live PostgreSQL database against `backend/app/models/` and Alembic migrations:

| SQLAlchemy Model | Model Column Count | DB Column Count | Missing in DB | Missing in Model | Consistency Status |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **`User`** (`app/models/user.py`) | 15 | 15 | None | None | 🟢 100% Match |
| **`Camera`** (`app/models/camera.py`) | 9 | 9 | None | None | 🟢 100% Match |
| **`Zone`** (`app/models/zone.py`) | 8 | 8 | None | None | 🟢 100% Match |
| **`Event`** (`app/models/event.py`) | 13 | 13 | None | None | 🟢 100% Match |
| **`Alert`** (`app/models/alert.py`) | 8 | 8 | None | None | 🟢 100% Match |
| **`Evidence`** (`app/models/evidence.py`) | 8 | 8 | None | None | 🟢 100% Match |
| **`AuditLog`** (`app/models/audit_log.py`) | 7 | 7 | None | None | 🟢 100% Match |

* **Alembic Revision Synchronization:** Live database `alembic_version` is `1fd6abcb82e2`, exactly matching the head Alembic migration script in `backend/migrations/versions/`.

---

## 13. Requirements Cross-Check

The live database schema and active records fully satisfy every step of the end-to-end autonomous surveillance pipeline:

$$\text{Video Ingestion} \longrightarrow \text{YOLO Detection} \longrightarrow \text{ByteTrack} \longrightarrow \text{Polygon Zone} \longrightarrow \text{Event} \longrightarrow \text{Alert} \longrightarrow \text{Evidence} \longrightarrow \text{SHA-256} \longrightarrow \text{Audit Log}$$

* **Detection & Tracking Data:** Captured in `events.bounding_box`, `events.position`, `events.track_id`.
* **Spatial Geofencing:** Captured in `zones.polygon_coordinates` (normalized 2D vertices).
* **Alarm Push & Triage:** Captured in `alerts.status`, `alerts.acknowledged_by`, `alerts.acknowledged_at`.
* **Forensic Chain of Custody:** Captured in `evidence.sha256_hash` (immutable 64-char hexadecimal digest).
* **Accountability:** Captured in `audit_logs` (immutable actor, action, resource, timestamp).

---

## 14. Final Verdict Scorecard

```text
DATABASE CONNECTIVITY:              PASS
CORE TABLES:
  users                             PASS
  cameras                           PASS
  zones                             PASS
  events                            PASS
  alerts                            PASS
  evidence                          PASS
  audit_logs                        PASS

RBAC DATA:                          PASS
EVENT → ALERT RELATIONSHIP:         PASS
EVENT IDEMPOTENCY:                  PASS
EVIDENCE SHA-256:                   PASS
AUDIT TRAIL:                        PASS
FOREIGN KEY INTEGRITY:              PASS
DATABASE ↔ SQLAlchemy CONSISTENCY:  PASS
DATABASE ↔ ALEMBIC CONSISTENCY:     PASS

================================================================================
FINAL STATUS:
🟢 COMPLETE (0 Gaps Found / 100% Verified)
================================================================================
```
