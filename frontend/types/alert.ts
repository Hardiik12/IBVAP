import { EventSeverity, EventType } from "./event";

export interface WebSocketAlertMessage {
  type: "NEW_ALERT" | "HEARTBEAT" | "SYSTEM_STATUS";
  alert_id: string;
  event_id: string;
  event_type: EventType;
  camera_id: string;
  camera_name?: string;
  zone_name: string;
  track_id: number;
  class_name?: string;
  confidence?: number;
  severity: EventSeverity;
  timestamp: string;
  evidence_id: string;
  bbox?: [number, number, number, number];
}

export interface AlertState extends WebSocketAlertMessage {
  isRead: boolean;
  acknowledgedAt?: string;
}
