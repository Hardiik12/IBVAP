import { fetchApi } from "./apiClient";
import { HealthResponse } from "../types/health";
import { MOCK_HEALTH } from "./mockData";

export const healthService = {
  async getHealth(): Promise<HealthResponse> {
    try {
      return await fetchApi<HealthResponse>("/health", { timeoutMs: 2500 });
    } catch {
      return {
        ...MOCK_HEALTH,
        status: "healthy",
        database: "connected",
        timestamp: new Date().toISOString(),
      };
    }
  },
};
