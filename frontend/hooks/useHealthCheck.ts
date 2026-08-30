"use client";

import { useEffect, useState, useCallback } from "react";
import { HealthResponse } from "../types/health";
import { healthService } from "../services/healthService";

export function useHealthCheck(pollIntervalMs = 5000) {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [isHealthy, setIsHealthy] = useState(false);

  const check = useCallback(async () => {
    try {
      const data = await healthService.getHealth();
      setHealth(data);
      const isOk =
        (data.status === "healthy" || data.status === "ok") &&
        (data.database === "connected" || !data.database);
      setIsHealthy(isOk);
    } catch {
      setHealth({
        status: "offline",
        service: "IBVAP Backend",
        version: "offline",
        database: "disconnected",
        timestamp: new Date().toISOString(),
      });
      setIsHealthy(false);
    }
  }, []);

  useEffect(() => {
    check();
    const interval = setInterval(check, pollIntervalMs);
    return () => clearInterval(interval);
  }, [check, pollIntervalMs]);

  return { health, isHealthy, refetch: check };
}
