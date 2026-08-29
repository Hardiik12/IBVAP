"use client";

import React, { useState, useEffect } from "react";
import { LiveVideoPlayer } from "../components/camera/LiveVideoPlayer";
import { TacticalStack } from "../components/alerts/TacticalStack";
import { TacticalFooter } from "../components/layout/TacticalFooter";
import { useCameraContext } from "../context/CameraContext";
import { useAlerts } from "../hooks/useAlerts";
import { useWebSocket } from "../hooks/useWebSocket";
import { eventService } from "../services/eventService";
import { IntrusionEvent } from "../types/event";
import { formatDate } from "../utils/formatters";
import { ShieldAlert, FileSearch } from "lucide-react";
import { Badge } from "../components/ui/Badge";

export default function DashboardPage() {
  const { zones } = useCameraContext();
  const { alerts, addAlert, openEvidenceModal } = useAlerts();
  const [recentEvents, setRecentEvents] = useState<IntrusionEvent[]>([]);

  // Connect WebSocket with automatic mock simulation fallback
  const { isConnected, triggerTestAlert } = useWebSocket({
    onMessage: (msg) => {
      addAlert(msg);
    },
  });

  useEffect(() => {
    const loadEvents = async () => {
      const data = await eventService.getEvents({ limit: 4 });
      setRecentEvents(data.slice(0, 4));
    };
    loadEvents();
  }, [alerts]);

  return (
    <div className="space-y-4 animate-fade-in flex flex-col justify-between min-h-[calc(100vh-6.5rem)]">
      {/* Main Tactical Grid Split: 75% Camera Viewport on Left, 25% Tactical Stack on Right */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-3.5 flex-1">
        {/* Left 9 Cols (75%): Dominant Live Surveillance Viewport + Active Zones */}
        <div className="lg:col-span-9 space-y-2.5 flex flex-col justify-between">
          <LiveVideoPlayer />

          {/* Active Restricted Zones Pill Bar */}
          <div className="surveillance-card py-2 px-3 rounded-lg border border-white/10 bg-surface-200/80 flex items-center justify-between text-xs font-mono">
            <div className="flex items-center gap-2">
              <span className="text-slate-400 font-bold">ACTIVE SECTORS:</span>
              {zones.map((z) => (
                <span
                  key={z.id}
                  className="px-2 py-0.5 rounded bg-amber-950/40 border border-amber-600/50 text-amber-300 text-[11px]"
                >
                  ⚠️ {z.name}
                </span>
              ))}
            </div>
            <span className="text-slate-500 text-[10px] hidden sm:inline">
              SHAPELY RAY-CASTING POINT-IN-POLYGON (PIP)
            </span>
          </div>
        </div>

        {/* Right 3 Cols (25%): Tactical Threat Level & Feed Stack */}
        <div className="lg:col-span-3 flex flex-col">
          <TacticalStack />
        </div>
      </div>


      {/* Footer Status Bar (4-Column Status Grid) */}
      <TacticalFooter />
    </div>
  );
}
