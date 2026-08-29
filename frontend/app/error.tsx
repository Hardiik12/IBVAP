"use client";

import React, { useEffect } from "react";
import { ShieldAlert, RotateCcw } from "lucide-react";
import { Button } from "../components/ui/Button";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("Dashboard error boundary caught:", error);
  }, [error]);

  return (
    <div className="h-[70vh] flex flex-col items-center justify-center text-center p-6 space-y-4">
      <div className="w-16 h-16 rounded-full bg-red-950/80 border border-red-800 flex items-center justify-center text-red-400">
        <ShieldAlert className="w-8 h-8" />
      </div>
      <h2 className="text-xl font-bold text-slate-100">Telemetry Stream Error</h2>
      <p className="text-sm font-mono text-slate-400 max-w-md">
        An unexpected error occurred while rendering the operational telemetry dashboard.
      </p>
      <Button
        variant="primary"
        onClick={() => reset()}
        leftIcon={<RotateCcw className="w-4 h-4" />}
      >
        Reload Operational Feed
      </Button>
    </div>
  );
}
