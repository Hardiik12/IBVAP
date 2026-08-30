import { fetchApi } from "./apiClient";
import { IntrusionEvent, EventQueryParams } from "../types/event";
import { MOCK_EVENTS } from "./mockData";

export const eventService = {
  async getEvents(params: EventQueryParams = {}): Promise<IntrusionEvent[]> {
    try {
      const query = new URLSearchParams();
      if (params.camera_id) query.append("camera_id", params.camera_id);
      if (params.event_type) query.append("event_type", params.event_type);
      if (params.severity) query.append("severity", params.severity);
      if (params.limit) query.append("limit", params.limit.toString());
      if (params.offset) query.append("offset", params.offset.toString());

      const qs = query.toString() ? `?${query.toString()}` : "";
      return await fetchApi<IntrusionEvent[]>(`/events${qs}`);
    } catch {
      console.warn("[eventService] Using fallback mock events");
      let filtered = [...MOCK_EVENTS];
      if (params.camera_id) {
        filtered = filtered.filter((e) => e.camera_id === params.camera_id);
      }
      if (params.severity) {
        filtered = filtered.filter((e) => e.severity === params.severity);
      }
      return filtered;
    }
  },

  async clearEvents(): Promise<{ message: string; cleared_count: number }> {
    return await fetchApi<{ message: string; cleared_count: number }>("/events", {
      method: "DELETE",
    });
  },
};
