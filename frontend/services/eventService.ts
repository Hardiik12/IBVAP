import { fetchApi } from "./apiClient";
import { IntrusionEvent, EventQueryParams } from "../types/event";

export const eventService = {
  async getEvents(params: EventQueryParams = {}): Promise<IntrusionEvent[]> {
    const query = new URLSearchParams();
    if (params.camera_id) query.append("camera_id", params.camera_id);
    if (params.event_type) query.append("event_type", params.event_type);
    if (params.severity) query.append("severity", params.severity);
    if (params.limit) query.append("limit", params.limit.toString());
    if (params.offset) query.append("offset", params.offset.toString());

    const qs = query.toString() ? `?${query.toString()}` : "";
    const rawEvents = await fetchApi<any[]>(`/events${qs}`);

    return rawEvents.map((e) => ({
      event_id: e.id,
      camera_id: e.camera_id,
      zone_id: e.zone_id,
      zone_name: e.metadata?.zone_name || e.event_metadata?.zone_name || "Perimeter Restricted Zone",
      event_type: e.event_type,
      track_id: e.track_id,
      class_name: e.metadata?.class_name || e.event_metadata?.class_name || "person",
      confidence: e.metadata?.confidence || e.event_metadata?.confidence || 0.85,
      severity: e.severity,
      timestamp: e.timestamp,
      bbox: e.bounding_box || [0.1, 0.2, 0.3, 0.4],
      evidence_id: e.metadata?.evidence_id || e.event_metadata?.evidence_id || e.id,
      acknowledged: e.status === "ACKNOWLEDGED" || e.status === "RESOLVED",
    }));
  },

  async getEvent(eventId: string): Promise<IntrusionEvent> {
    const e = await fetchApi<any>(`/events/${eventId}`);
    return {
      event_id: e.id,
      camera_id: e.camera_id,
      zone_id: e.zone_id,
      zone_name: e.metadata?.zone_name || e.event_metadata?.zone_name || "Perimeter Restricted Zone",
      event_type: e.event_type,
      track_id: e.track_id,
      class_name: e.metadata?.class_name || e.event_metadata?.class_name || "person",
      confidence: e.metadata?.confidence || e.event_metadata?.confidence || 0.85,
      severity: e.severity,
      timestamp: e.timestamp,
      bbox: e.bounding_box || [0.1, 0.2, 0.3, 0.4],
      evidence_id: e.metadata?.evidence_id || e.event_metadata?.evidence_id || e.id,
      acknowledged: e.status === "ACKNOWLEDGED" || e.status === "RESOLVED",
    };
  },

  async clearEvents(): Promise<{ message: string; cleared_count: number }> {
    return await fetchApi<{ message: string; cleared_count: number }>("/events", {
      method: "DELETE",
    });
  },
};
