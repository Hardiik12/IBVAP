"use client";

import React, { useState, useEffect } from "react";
import { SystemStatusBadge } from "./SystemStatusBadge";
import { useAlerts } from "../../hooks/useAlerts";
import { useCameraContext } from "../../context/CameraContext";
import {
  Volume2,
  VolumeX,
  Shield,
  Video,
  Sparkles,
} from "lucide-react";
import { Button } from "../ui/Button";

interface HeaderProps {
  onTriggerTestAlert?: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onTriggerTestAlert }) => {
  const { isAudioMuted, toggleAudioMute } = useAlerts();
  const { cameras, selectedCamera, selectCamera } = useCameraContext();

  const [mounted, setMounted] = useState(false);
  const [time, setTime] = useState<string>("14:27:36");

  useEffect(() => {
    setMounted(true);
    const updateTime = () => {
      const now = new Date();
      setTime(
        now.toLocaleTimeString("en-US", {
          hour12: false,
          hour: "2-digit",
          minute: "2-digit",
          second: "2-digit",
        })
      );
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="h-14 px-5 border-b border-white/10 bg-surface-300/90 backdrop-blur-md flex items-center justify-between sticky top-0 z-30 font-mono text-xs">
      {/* Center/Left Tactical Header Pill (As seen in image_2.png) */}
      <div className="flex items-center gap-3 bg-surface-100/90 border border-white/15 px-4 py-2 rounded-lg shadow-inner">
        <div className="flex items-center gap-2 font-bold text-slate-100 tracking-wider">
          <Shield className="w-4 h-4 text-blue-400" />
          <span>BORDER SECURITY AI</span>
        </div>

        <span className="text-slate-600">|</span>

        <div className="hidden sm:flex items-center gap-2 text-slate-300 text-[11px]">
          <span>SECTOR: <strong className="text-slate-100">KOLKATA FRONTIER</strong></span>
          <span className="text-slate-600">|</span>
          <span>OPERATOR: <strong className="text-slate-100">BSF-07</strong></span>
        </div>

        <span className="text-slate-600">|</span>

        <div className="text-slate-300 text-[11px]">
          UTC: <strong className="text-emerald-400" suppressHydrationWarning>{time}</strong>
        </div>
      </div>

      {/* Right Controls: Camera Selection, Audio, Simulation */}
      <div className="flex items-center gap-3">
        {/* Camera Selector */}
        <div className="flex items-center gap-2">
          <Video className="w-3.5 h-3.5 text-blue-400" />
          <select
            value={selectedCamera?.id || ""}
            onChange={(e) => selectCamera(e.target.value)}
            className="bg-surface-100 border border-white/15 text-slate-200 text-xs font-mono rounded px-2 py-1 focus:outline-none focus:border-blue-500 cursor-pointer"
          >
            {cameras.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </div>

        {/* Demo Simulation Action Button */}
        {onTriggerTestAlert && (
          <Button
            size="sm"
            variant="outline"
            onClick={onTriggerTestAlert}
            className="text-[11px] py-1 border-amber-800/60 bg-amber-950/20 text-amber-300 hover:bg-amber-900/40"
            leftIcon={<Sparkles className="w-3 h-3 text-amber-400" />}
          >
            Simulate Alert
          </Button>
        )}

        {/* Audio Alert Toggle */}
        <button
          onClick={toggleAudioMute}
          title={isAudioMuted ? "Unmute Alerts" : "Mute Alerts"}
          className={`p-1.5 rounded border transition ${
            isAudioMuted
              ? "bg-surface-100 border-white/10 text-slate-500 hover:text-slate-300"
              : "bg-blue-600/10 border-blue-500/30 text-blue-400 hover:bg-blue-600/20"
          }`}
        >
          {isAudioMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
        </button>

        {/* System Health Status */}
        <SystemStatusBadge />
      </div>
    </header>
  );
};
