import { fetchApi } from "./apiClient";
import { HealthResponse } from "../types/health";

export const healthService = {
  async getHealth(): Promise<HealthResponse> {
    try {
      return await fetchApi<HealthResponse>("/health", { timeoutMs: 2500, skipAuth: true });
    } catch {
      return {
        status: "offline",
        service: "IBVAP Backend",
        version: "offline",
        database: "disconnected",
        timestamp: new Date().toISOString(),
      };
    }
  },
};
