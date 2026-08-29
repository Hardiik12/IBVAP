export interface HealthResponse {
  status: "healthy" | "degraded" | "unhealthy";
  version: string;
  database: "connected" | "disconnected" | "error";
  ai_pipeline?: "running" | "idle" | "error";
  timestamp: string;
  fps?: number;
  active_cameras?: number;
}
