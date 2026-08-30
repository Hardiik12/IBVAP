import { fetchApi } from "./apiClient";
import { Camera } from "../types/camera";
import { Zone } from "../types/zone";

export const cameraService = {
  async getCameras(): Promise<Camera[]> {
    const rawCameras = await fetchApi<any[]>("/cameras");
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
  },

  async getCamera(cameraId: string): Promise<Camera> {
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
  },

  async getCameraZones(cameraId: string): Promise<Zone[]> {
    const rawZones = await fetchApi<any[]>(`/cameras/${cameraId}/zones`);
    return rawZones.map((z) => ({
      id: z.id,
      camera_id: z.camera_id,
      name: z.name,
      polygon: z.polygon || z.polygon_coordinates || [],
      color: z.color || "#f59e0b",
      created_at: z.created_at || new Date().toISOString(),
    }));
  },
};
