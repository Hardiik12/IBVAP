-- ==============================================================================
-- IBVAP — Intelligent Border Video Analytics Platform
-- Complete PostgreSQL Database Schema Definition for pgAdmin / DDL Reproduction
-- ==============================================================================
-- Database Target: PostgreSQL 15+
-- Schema: public
-- Character Set: UTF8
-- Generated: 2026-08-30
-- Description: Complete structural DDL definition matching live IBVAP database.
-- NOTE: Contains structure only. Zero credentials or sensitive data.
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- 1. EXTENSIONS & ENUM TYPES
-- ------------------------------------------------------------------------------

-- User Roles for Role-Based Access Control (RBAC)
CREATE TYPE userrole AS ENUM (
    'OPERATOR',
    'ANALYST',
    'ADMINISTRATOR',
    'AUDITOR'
);

-- Camera Stream Ingestion Types
CREATE TYPE camerasourcetype AS ENUM (
    'WEBCAM',
    'VIDEO_FILE',
    'RTSP'
);

-- Virtual Perimeter Zone Geofencing Types
CREATE TYPE zonetype AS ENUM (
    'RESTRICTED',
    'MONITORED'
);

-- Intrusion & AI Event Classification Types
CREATE TYPE eventtype AS ENUM (
    'INTRUSION',
    'EXIT',
    'LOITERING',
    'UNAUTHORIZED_VEHICLE'
);

-- Alert & Event Severity Levels
CREATE TYPE eventseverity AS ENUM (
    'LOW',
    'MEDIUM',
    'HIGH',
    'CRITICAL'
);

-- Event Pipeline Lifecycle Status
CREATE TYPE eventstatus AS ENUM (
    'NEW',
    'PROCESSED',
    'ARCHIVED'
);

-- Real-Time Security Alert Operational States
CREATE TYPE alertstatus AS ENUM (
    'ACTIVE',
    'ACKNOWLEDGED',
    'RESOLVED'
);

-- ------------------------------------------------------------------------------
-- 2. TABLE DEFINITIONS
-- ------------------------------------------------------------------------------

-- Table: alembic_version (Schema Migration Tracking)
CREATE TABLE IF NOT EXISTS alembic_version (
    version_num VARCHAR(32) NOT NULL,
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Table: users (Authentication, RBAC, TOTP MFA, and Face Biometrics)
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(36) NOT NULL,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role userrole NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    mfa_secret VARCHAR(64) NULL,
    mfa_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    face_embedding TEXT NULL,
    face_enrolled BOOLEAN NOT NULL DEFAULT FALSE,
    face_enrolled_at TIMESTAMP WITH TIME ZONE NULL,
    failed_login_attempts INTEGER NOT NULL DEFAULT 0,
    locked_until TIMESTAMP WITH TIME ZONE NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    CONSTRAINT users_pkey PRIMARY KEY (id)
);

-- Table: cameras (Video Ingestion Sensors & Hardware Configuration)
CREATE TABLE IF NOT EXISTS cameras (
    id VARCHAR(36) NOT NULL,
    name VARCHAR(100) NOT NULL,
    camera_identifier VARCHAR(50) NOT NULL,
    source_type camerasourcetype NOT NULL,
    source_url VARCHAR(255) NULL,
    location VARCHAR(100) NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    CONSTRAINT cameras_pkey PRIMARY KEY (id)
);

-- Table: zones (Virtual Polygon Geofence Coordinates per Camera)
CREATE TABLE IF NOT EXISTS zones (
    id VARCHAR(36) NOT NULL,
    camera_id VARCHAR(36) NOT NULL,
    name VARCHAR(100) NOT NULL,
    zone_type zonetype NOT NULL,
    polygon_coordinates JSON NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    CONSTRAINT zones_pkey PRIMARY KEY (id),
    CONSTRAINT zones_camera_id_fkey FOREIGN KEY (camera_id)
        REFERENCES cameras (id) ON DELETE CASCADE
);

-- Table: events (AI-Generated Intrusion Events with Track IDs and Bounding Boxes)
CREATE TABLE IF NOT EXISTS events (
    id VARCHAR(36) NOT NULL,
    event_identifier VARCHAR(50) NOT NULL,
    event_type eventtype NOT NULL,
    camera_id VARCHAR(36) NOT NULL,
    zone_id VARCHAR(36) NULL,
    track_id INTEGER NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    severity eventseverity NOT NULL,
    status eventstatus NOT NULL DEFAULT 'NEW',
    bounding_box JSON NULL,
    position JSON NULL,
    event_metadata JSON NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    CONSTRAINT events_pkey PRIMARY KEY (id),
    CONSTRAINT events_camera_id_fkey FOREIGN KEY (camera_id)
        REFERENCES cameras (id) ON DELETE NO ACTION,
    CONSTRAINT events_zone_id_fkey FOREIGN KEY (zone_id)
        REFERENCES zones (id) ON DELETE NO ACTION
);

-- Table: alerts (Real-Time Operator Push Alarms & Acknowledgement Logs)
CREATE TABLE IF NOT EXISTS alerts (
    id VARCHAR(36) NOT NULL,
    event_id VARCHAR(36) NOT NULL,
    severity eventseverity NOT NULL,
    status alertstatus NOT NULL DEFAULT 'ACTIVE',
    message VARCHAR(255) NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    acknowledged_at TIMESTAMP WITH TIME ZONE NULL,
    acknowledged_by VARCHAR(36) NULL,
    CONSTRAINT alerts_pkey PRIMARY KEY (id),
    CONSTRAINT alerts_event_id_fkey FOREIGN KEY (event_id)
        REFERENCES events (id) ON DELETE CASCADE,
    CONSTRAINT alerts_acknowledged_by_fkey FOREIGN KEY (acknowledged_by)
        REFERENCES users (id) ON DELETE NO ACTION
);

-- Table: evidence (Forensic Frame Snapshots & SHA-256 Checksums)
CREATE TABLE IF NOT EXISTS evidence (
    id VARCHAR(36) NOT NULL,
    evidence_identifier VARCHAR(50) NOT NULL,
    event_id VARCHAR(36) NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    sha256_hash VARCHAR(64) NULL,
    captured_at TIMESTAMP WITH TIME ZONE NOT NULL,
    evidence_metadata JSON NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    CONSTRAINT evidence_pkey PRIMARY KEY (id),
    CONSTRAINT evidence_event_id_fkey FOREIGN KEY (event_id)
        REFERENCES events (id) ON DELETE RESTRICT
);

-- Table: audit_logs (Immutable Forensic Security Trail)
CREATE TABLE IF NOT EXISTS audit_logs (
    id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id VARCHAR(50) NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    log_metadata JSON NULL,
    CONSTRAINT audit_logs_pkey PRIMARY KEY (id),
    CONSTRAINT audit_logs_user_id_fkey FOREIGN KEY (user_id)
        REFERENCES users (id) ON DELETE NO ACTION
);

-- ------------------------------------------------------------------------------
-- 3. UNIQUE CONSTRAINTS & PERFORMANCE INDEXES
-- ------------------------------------------------------------------------------

-- Users Indexes
CREATE UNIQUE INDEX IF NOT EXISTS ix_users_username ON users (username);
CREATE UNIQUE INDEX IF NOT EXISTS ix_users_email ON users (email);

-- Cameras Indexes
CREATE UNIQUE INDEX IF NOT EXISTS ix_cameras_camera_identifier ON cameras (camera_identifier);

-- Zones Indexes
CREATE INDEX IF NOT EXISTS ix_zones_camera_id ON zones (camera_id);

-- Events Indexes
CREATE UNIQUE INDEX IF NOT EXISTS ix_events_event_identifier ON events (event_identifier);
CREATE INDEX IF NOT EXISTS ix_events_camera_id ON events (camera_id);
CREATE INDEX IF NOT EXISTS ix_events_zone_id ON events (zone_id);
CREATE INDEX IF NOT EXISTS ix_events_event_type ON events (event_type);
CREATE INDEX IF NOT EXISTS ix_events_timestamp ON events (timestamp);
CREATE INDEX IF NOT EXISTS idx_events_camera_timestamp ON events (camera_id, timestamp);

-- Alerts Indexes
CREATE UNIQUE INDEX IF NOT EXISTS ix_alerts_event_id ON alerts (event_id);
CREATE INDEX IF NOT EXISTS ix_alerts_status ON alerts (status);

-- Evidence Indexes
CREATE UNIQUE INDEX IF NOT EXISTS ix_evidence_evidence_identifier ON evidence (evidence_identifier);
CREATE INDEX IF NOT EXISTS ix_evidence_event_id ON evidence (event_id);
CREATE INDEX IF NOT EXISTS ix_evidence_sha256_hash ON evidence (sha256_hash);

-- Audit Logs Indexes
CREATE INDEX IF NOT EXISTS ix_audit_logs_user_id ON audit_logs (user_id);
CREATE INDEX IF NOT EXISTS ix_audit_logs_timestamp ON audit_logs (timestamp);

-- ==============================================================================
-- End of Schema Definition
-- ==============================================================================
