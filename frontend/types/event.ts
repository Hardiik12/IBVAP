export type EventType = "INTRUSION" | "ZONE_ENTRY" | "ZONE_EXIT" | "LOITERING";
export type EventSeverity = "HIGH" | "MEDIUM" | "LOW" | "CRITICAL";

/**
 * Bounding box in raw or normalized coordinates [x1, y1, x2, y2]
 */
export type BoundingBox = [number, number, number, number];

export interface IntrusionEvent {
  event_id: string;
  camera_id: string;
  zone_id: string;
  zone_name?: string;
  event_type: EventType;
  track_id: number;
  class_name: string;
  confidence: number;
  severity: EventSeverity;
  timestamp: string;
  bbox: BoundingBox;
  evidence_id?: string;
  evidence_snapshot?: string;
  acknowledged?: boolean;
}

export interface EventQueryParams {
  camera_id?: string;
  event_type?: EventType;
  severity?: EventSeverity;
  limit?: number;
  offset?: number;
}
