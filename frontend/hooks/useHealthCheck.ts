"use client";

import { useEffect, useState, useCallback } from "react";
import { HealthResponse } from "../types/health";
import { healthService } from "../services/healthService";

export function useHealthCheck(pollIntervalMs = 5000) {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [isHealthy, setIsHealthy] = useState(true);

  const check = useCallback(async () => {
    const data = await healthService.getHealth();
    setHealth(data);
    setIsHealthy(
      (data.status === "healthy" || data.status === "ok") &&
      (data.database === "connected" || data.database === "ok" || !data.database)
    );

  }, []);

  useEffect(() => {
    check();
    const interval = setInterval(check, pollIntervalMs);
    return () => clearInterval(interval);
  }, [check, pollIntervalMs]);

  return { health, isHealthy, refetch: check };
}
