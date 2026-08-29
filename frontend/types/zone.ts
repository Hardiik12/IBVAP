/**
 * Normalized 2D coordinate [x, y] where 0.0 <= x <= 1.0 and 0.0 <= y <= 1.0
 */
export type PolygonPoint = [number, number];

export interface Zone {
  id: string;
  camera_id: string;
  name: string;
  polygon: PolygonPoint[];
  color?: string;
  created_at: string;
}
