import { fetchApi } from "./apiClient";
import { Camera } from "../types/camera";
import { Zone } from "../types/zone";
import { MOCK_CAMERAS, MOCK_ZONES } from "./mockData";

export const cameraService = {
  async getCameras(): Promise<Camera[]> {
    try {
      return await fetchApi<Camera[]>("/cameras");
    } catch {
      console.warn("[cameraService] Using fallback mock cameras");
      return MOCK_CAMERAS;
    }
  },

  async getCameraZones(cameraId: string): Promise<Zone[]> {
    try {
      return await fetchApi<Zone[]>(`/cameras/${cameraId}/zones`);
    } catch {
      console.warn(`[cameraService] Using fallback mock zones for ${cameraId}`);
      return MOCK_ZONES.filter((z) => z.camera_id === cameraId || z.camera_id === "cam-01");
    }
  },
};
