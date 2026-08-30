export interface HealthResponse {
  status: "healthy" | "degraded" | "unhealthy" | "ok" | "offline";
  service?: string;
  version?: string;
  database?: "connected" | "disconnected" | "error" | "offline" | string;
  ai_pipeline?: "running" | "idle" | "error" | "offline" | string;
  timestamp?: string;
  fps?: number;
  active_cameras?: number;
}
