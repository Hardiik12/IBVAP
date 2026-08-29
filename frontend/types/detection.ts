export interface AIDetectionItem {
  track_id: number;
  class_id: number;
  class_name: string;
  confidence: number;
  bbox: [number, number, number, number]; // normalized [x1, y1, x2, y2] (0.0 - 1.0)
  reference_point: [number, number]; // normalized [x, y] (0.0 - 1.0)
  is_inside_zone: boolean;
  zone_id?: string;
  zone_name?: string;
}

export interface AIDetectionResponse {
  detections: AIDetectionItem[];
  inference_ms: number;
  frame_width: number;
  frame_height: number;
  total_objects: number;
}
