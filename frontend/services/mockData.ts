import { Camera } from "../types/camera";
import { Zone } from "../types/zone";
import { IntrusionEvent } from "../types/event";
import { WebSocketAlertMessage } from "../types/alert";
import { EvidenceRecord } from "../types/evidence";
import { HealthResponse } from "../types/health";

export const MOCK_CAMERAS: Camera[] = [
  {
    id: "cam-01",
    name: "Perimeter Sector Alpha (Webcam)",
    source_type: "webcam",
    source_index: 0,
    status: "ACTIVE",
    resolution: "1280x720",
    fps: 30,
    created_at: new Date(Date.now() - 3600000 * 24).toISOString(),
  },
  {
    id: "cam-02",
    name: "North Gate Entrance (Test Stream)",
    source_type: "video_file",
    source_index: "data/test_videos/sample_patrol.mp4",
    status: "ACTIVE",
    resolution: "1920x1080",
    fps: 25,
    created_at: new Date(Date.now() - 3600000 * 12).toISOString(),
  },
  {
    id: "cam-03",
    name: "South Fence Boundary (Backup)",
    source_type: "phone",
    source_index: "http://192.168.1.105:8080/video",
    status: "OFFLINE",
    resolution: "1280x720",
    fps: 0,
    created_at: new Date(Date.now() - 3600000 * 48).toISOString(),
  },
];

export const MOCK_ZONES: Zone[] = [
  {
    id: "zone-alpha",
    camera_id: "cam-01",
    name: "Perimeter Exclusion Zone 1",
    polygon: [
      [0.2, 0.25],
      [0.8, 0.25],
      [0.85, 0.85],
      [0.15, 0.85],
    ],
    color: "#f59e0b",
    created_at: new Date(Date.now() - 3600000 * 20).toISOString(),
  },
  {
    id: "zone-bravo",
    camera_id: "cam-02",
    name: "Restricted Gate Area B",
    polygon: [
      [0.35, 0.3],
      [0.65, 0.3],
      [0.75, 0.9],
      [0.25, 0.9],
    ],
    color: "#ef4444",
    created_at: new Date(Date.now() - 3600000 * 10).toISOString(),
  },
];

export const MOCK_EVENTS: IntrusionEvent[] = [
  {
    event_id: "evt-99201",
    camera_id: "cam-01",
    zone_id: "zone-alpha",
    zone_name: "Perimeter Exclusion Zone 1",
    event_type: "INTRUSION",
    track_id: 17,
    class_name: "person",
    confidence: 0.94,
    severity: "HIGH",
    timestamp: new Date(Date.now() - 1000 * 45).toISOString(),
    bbox: [0.42, 0.38, 0.58, 0.78],
    evidence_id: "evi-33104",
  },
  {
    event_id: "evt-99202",
    camera_id: "cam-01",
    zone_id: "zone-alpha",
    zone_name: "Perimeter Exclusion Zone 1",
    event_type: "INTRUSION",
    track_id: 22,
    class_name: "person",
    confidence: 0.89,
    severity: "CRITICAL",
    timestamp: new Date(Date.now() - 1000 * 180).toISOString(),
    bbox: [0.25, 0.32, 0.41, 0.74],
    evidence_id: "evi-33105",
  },
  {
    event_id: "evt-99203",
    camera_id: "cam-02",
    zone_id: "zone-bravo",
    zone_name: "Restricted Gate Area B",
    event_type: "INTRUSION",
    track_id: 31,
    class_name: "vehicle",
    confidence: 0.96,
    severity: "MEDIUM",
    timestamp: new Date(Date.now() - 1000 * 600).toISOString(),
    bbox: [0.38, 0.45, 0.62, 0.82],
    evidence_id: "evi-33106",
  },
  {
    event_id: "evt-99204",
    camera_id: "cam-01",
    zone_id: "zone-alpha",
    zone_name: "Perimeter Exclusion Zone 1",
    event_type: "INTRUSION",
    track_id: 14,
    class_name: "person",
    confidence: 0.91,
    severity: "HIGH",
    timestamp: new Date(Date.now() - 1000 * 1200).toISOString(),
    bbox: [0.65, 0.35, 0.78, 0.8],
    evidence_id: "evi-33107",
  },
];

export const MOCK_EVIDENCE: Record<string, EvidenceRecord> = {
  "evi-33104": {
    evidence_id: "evi-33104",
    event_id: "evt-99201",
    camera_id: "cam-01",
    file_path: "/data/evidence/evi-33104.jpg",
    sha256_hash: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    captured_at: new Date(Date.now() - 1000 * 45).toISOString(),
    image_url: "/placeholder-feed.jpg",
    verified_status: "UNKNOWN",
  },
  "evi-33105": {
    evidence_id: "evi-33105",
    event_id: "evt-99202",
    camera_id: "cam-01",
    file_path: "/data/evidence/evi-33105.jpg",
    sha256_hash: "a4f5c9e2b1d34567890abcdef1234567890abcdef1234567890abcdef1234567",
    captured_at: new Date(Date.now() - 1000 * 180).toISOString(),
    image_url: "/placeholder-feed.jpg",
    verified_status: "VERIFIED",
  },
  "evi-33106": {
    evidence_id: "evi-33106",
    event_id: "evt-99203",
    camera_id: "cam-02",
    file_path: "/data/evidence/evi-33106.jpg",
    sha256_hash: "7c98f12a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e",
    captured_at: new Date(Date.now() - 1000 * 600).toISOString(),
    image_url: "/placeholder-feed.jpg",
    verified_status: "TAMPERED",
  },
  "evi-33107": {
    evidence_id: "evi-33107",
    event_id: "evt-99204",
    camera_id: "cam-01",
    file_path: "/data/evidence/evi-33107.jpg",
    sha256_hash: "1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e7c98f12a3b4c5d6e7f8a9b0c",
    captured_at: new Date(Date.now() - 1000 * 1200).toISOString(),
    image_url: "/placeholder-feed.jpg",
    verified_status: "UNKNOWN",
  },
};

export const MOCK_HEALTH: HealthResponse = {
  status: "healthy",
  version: "0.1.0-mvp",
  database: "connected",
  ai_pipeline: "running",
  timestamp: new Date().toISOString(),
  fps: 28.6,
  active_cameras: 2,
};

export function createMockAlert(trackId = Math.floor(Math.random() * 80) + 10): WebSocketAlertMessage {
  const eventId = `evt-${Math.floor(Math.random() * 90000) + 10000}`;
  const evidenceId = `evi-${Math.floor(Math.random() * 90000) + 10000}`;
  const severities = ["HIGH", "CRITICAL", "MEDIUM"] as const;
  const severity = severities[Math.floor(Math.random() * severities.length)];

  return {
    type: "NEW_ALERT",
    alert_id: `alt-${Math.floor(Math.random() * 90000) + 10000}`,
    event_id: eventId,
    event_type: "INTRUSION",
    camera_id: "cam-01",
    camera_name: "Perimeter Sector Alpha",
    zone_name: "Perimeter Exclusion Zone 1",
    track_id: trackId,
    class_name: "person",
    confidence: Number((0.85 + Math.random() * 0.12).toFixed(2)),
    severity: severity,
    timestamp: new Date().toISOString(),
    evidence_id: evidenceId,
    bbox: [0.35 + Math.random() * 0.2, 0.3 + Math.random() * 0.2, 0.5 + Math.random() * 0.2, 0.75 + Math.random() * 0.15],
  };
}
