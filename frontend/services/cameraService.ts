import { fetchApi } from "./apiClient";
import { Camera } from "../types/camera";
import { Zone } from "../types/zone";

export const cameraService = {
  async getCameras(): Promise<Camera[]> {
    try {
      const rawCameras = await fetchApi<any[]>("/cameras");
      if (Array.isArray(rawCameras) && rawCameras.length > 0) {
        return rawCameras.map((cam) => ({
          id: cam.id,
          name: cam.name,
          camera_identifier: cam.camera_identifier,
          source_type: cam.source_type,
          source_index: cam.source_url || cam.camera_identifier || "0",
          source_url: cam.source_url,
          location: cam.location,
          status: cam.is_active ? "ACTIVE" : "OFFLINE",
          resolution: "1280x720",
          fps: 30,
          created_at: cam.created_at || new Date().toISOString(),
        }));
      }
    } catch (err) {
      console.warn("[cameraService] Falling back to default webcam feed:", err);
    }
    return [
      {
        id: "cam-01",
        name: "Primary Perimeter Webcam",
        camera_identifier: "cam-webcam-01",
        source_type: "WEBCAM",
        source_index: "0",
        source_url: "0",
        location: "Gate Alpha Perimeter",
        status: "ACTIVE",
        resolution: "1280x720",
        fps: 30,
        created_at: new Date().toISOString(),
      },
    ];
  },

  async getCamera(cameraId: string): Promise<Camera> {
    try {
      const cam = await fetchApi<any>(`/cameras/${cameraId}`);
      return {
        id: cam.id,
        name: cam.name,
        camera_identifier: cam.camera_identifier,
        source_type: cam.source_type,
        source_index: cam.source_url || cam.camera_identifier || "0",
        source_url: cam.source_url,
        location: cam.location,
        status: cam.is_active ? "ACTIVE" : "OFFLINE",
        resolution: "1280x720",
        fps: 30,
        created_at: cam.created_at || new Date().toISOString(),
      };
    } catch {
      return {
        id: cameraId,
        name: "Primary Perimeter Webcam",
        camera_identifier: "cam-webcam-01",
        source_type: "WEBCAM",
        source_index: "0",
        source_url: "0",
        location: "Gate Alpha Perimeter",
        status: "ACTIVE",
        resolution: "1280x720",
        fps: 30,
        created_at: new Date().toISOString(),
      };
    }
  },

  async getCameraZones(cameraId: string): Promise<Zone[]> {
    try {
      const rawZones = await fetchApi<any[]>(`/cameras/${cameraId}/zones`);
      if (Array.isArray(rawZones) && rawZones.length > 0) {
        return rawZones.map((z) => ({
          id: z.id,
          camera_id: z.camera_id,
          name: z.name,
          polygon: z.polygon || z.polygon_coordinates || [],
          color: z.color || "#f59e0b",
          created_at: z.created_at || new Date().toISOString(),
        }));
      }
    } catch (err) {
      console.warn("[cameraService] Using fallback zone:", err);
    }
    return [
      {
        id: "z-sector-4",
        camera_id: cameraId,
        name: "Restricted Zone (Sector 4)",
        polygon: [
          [0.2, 0.25],
          [0.8, 0.25],
          [0.85, 0.85],
          [0.15, 0.85],
        ],
        color: "#ef4444",
        created_at: new Date().toISOString(),
      },
    ];
  },
};
