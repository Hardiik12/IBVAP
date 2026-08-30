export type CameraSourceType = "webcam" | "video_file" | "rtsp" | "phone" | "WEBCAM" | "VIDEO_FILE" | "RTSP";
export type CameraStatus = "ACTIVE" | "OFFLINE" | "ERROR";

export interface Camera {
  id: string;
  name: string;
  camera_identifier?: string;
  source_type: CameraSourceType;
  source_index?: number | string;
  source_url?: string;
  location?: string;
  is_active?: boolean;
  status: CameraStatus;
  resolution?: string;
  fps?: number;
  created_at: string;
}

