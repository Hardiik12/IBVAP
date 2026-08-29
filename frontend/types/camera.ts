export type CameraSourceType = "webcam" | "video_file" | "rtsp" | "phone";
export type CameraStatus = "ACTIVE" | "OFFLINE" | "ERROR";

export interface Camera {
  id: string;
  name: string;
  source_type: CameraSourceType;
  source_index: number | string;
  status: CameraStatus;
  resolution?: string;
  fps?: number;
  created_at: string;
}
