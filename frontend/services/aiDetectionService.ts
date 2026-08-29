import { AIDetectionResponse } from "../types/detection";
import { Zone } from "../types/zone";

interface DetectFrameOptions {
  image: string; // Base64 image
  cameraId?: string;
  confidenceThreshold?: number;
  zones?: Zone[];
}

export const aiDetectionService = {
  async detectFrame(options: DetectFrameOptions): Promise<AIDetectionResponse> {
    const { image, cameraId = "cam-01", confidenceThreshold = 0.3, zones = [] } = options;

    const payload = {
      image,
      camera_id: cameraId,
      confidence_threshold: confidenceThreshold,
      zones: zones.map((z) => ({
        id: z.id,
        name: z.name,
        polygon: z.polygon,
      })),
    };

    const response = await fetch("/api/v1/detection/detect", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error(`AI Detection request failed: ${response.status}`);
    }

    return (await response.json()) as AIDetectionResponse;
  },
};
