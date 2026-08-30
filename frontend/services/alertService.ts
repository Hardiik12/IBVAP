import { fetchApi } from "./apiClient";
import { AlertState, WebSocketAlertMessage } from "../types/alert";

export interface AlertQueryParams {
  status?: string;
  severity?: string;
  camera_id?: string;
  limit?: number;
  offset?: number;
}

export const alertService = {
  async getAlerts(params: AlertQueryParams = {}): Promise<AlertState[]> {
    const query = new URLSearchParams();
    if (params.status) query.append("status", params.status);
    if (params.severity) query.append("severity", params.severity);
    if (params.camera_id) query.append("camera_id", params.camera_id);
    if (params.limit) query.append("limit", params.limit.toString());
    if (params.offset) query.append("offset", params.offset.toString());

    const qs = query.toString() ? `?${query.toString()}` : "";
    const rawAlerts = await fetchApi<any[]>(`/alerts${qs}`);

    return rawAlerts.map((a) => ({
      type: "NEW_ALERT",
      alert_id: a.id,
      event_id: a.event_id,
      event_type: a.event?.event_type || "INTRUSION",
      camera_id: a.event?.camera_id || "cam-webcam-01",
      camera_name: a.event?.camera?.name || "Main Perimeter Camera 01",
      zone_name: a.event?.zone?.name || a.event?.event_metadata?.zone_name || "Perimeter Restricted Zone",
      track_id: a.event?.track_id || 1,
      class_name: a.event?.event_metadata?.class || "person",
      confidence: a.event?.event_metadata?.confidence || 0.9,
      severity: a.event?.severity || "CRITICAL",
      timestamp: a.event?.timestamp || a.created_at || new Date().toISOString(),
      evidence_id: a.event?.evidence?.[0]?.id || `evi-${a.event_id}`,
      bbox: a.event?.bounding_box || [0.2, 0.2, 0.4, 0.6],
      isRead: a.status === "ACKNOWLEDGED" || a.status === "RESOLVED",
      acknowledgedAt: a.acknowledged_at,
    }));
  },

  async getAlert(alertId: string): Promise<AlertState> {
    const a = await fetchApi<any>(`/alerts/${alertId}`);
    return {
      type: "NEW_ALERT",
      alert_id: a.id,
      event_id: a.event_id,
      event_type: a.event?.event_type || "INTRUSION",
      camera_id: a.event?.camera_id || "cam-webcam-01",
      camera_name: a.event?.camera?.name || "Main Perimeter Camera 01",
      zone_name: a.event?.zone?.name || a.event?.event_metadata?.zone_name || "Perimeter Restricted Zone",
      track_id: a.event?.track_id || 1,
      class_name: a.event?.event_metadata?.class || "person",
      confidence: a.event?.event_metadata?.confidence || 0.9,
      severity: a.event?.severity || "CRITICAL",
      timestamp: a.event?.timestamp || a.created_at || new Date().toISOString(),
      evidence_id: a.event?.evidence?.[0]?.id || `evi-${a.event_id}`,
      bbox: a.event?.bounding_box || [0.2, 0.2, 0.4, 0.6],
      isRead: a.status === "ACKNOWLEDGED" || a.status === "RESOLVED",
      acknowledgedAt: a.acknowledged_at,
    };
  },

  async acknowledgeAlert(alertId: string): Promise<any> {
    return await fetchApi<any>(`/alerts/${alertId}`, {
      method: "PATCH",
      body: JSON.stringify({ status: "ACKNOWLEDGED" }),
    });
  },
};
