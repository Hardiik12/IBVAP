"use client";

import React, { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { SystemStatusBadge } from "./SystemStatusBadge";
import { useAlerts } from "../../hooks/useAlerts";
import { useCameraContext } from "../../context/CameraContext";
import { useAuth } from "../../context/AuthContext";
import {
  Volume2,
  VolumeX,
  Shield,
  Video,
  Sparkles,
  User,
  LogOut,
  ShieldCheck,
  ChevronDown,
  Lock,
  Scan,
} from "lucide-react";
import { Button } from "../ui/Button";

interface HeaderProps {
  onTriggerTestAlert?: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onTriggerTestAlert }) => {
  const router = useRouter();
  const { isAudioMuted, toggleAudioMute } = useAlerts();
  const { cameras, selectedCamera, selectCamera } = useCameraContext();
  const { user, logout } = useAuth();

  const [mounted, setMounted] = useState(false);
  const [time, setTime] = useState<string>("00:00:00");
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const profileDropdownRef = useRef<HTMLDivElement>(null);

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

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        profileDropdownRef.current &&
        !profileDropdownRef.current.contains(event.target as Node)
      ) {
        setIsProfileOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleLogout = async () => {
    setIsProfileOpen(false);
    await logout();
    router.push("/login");
  };

  const username = user?.username ? user.username.toUpperCase() : "ADMIN";
  const role = user?.role || "ADMINISTRATOR";

  return (
    <header className="h-14 px-5 border-b border-white/10 bg-surface-300/90 backdrop-blur-md flex items-center justify-between sticky top-0 z-30 font-mono text-xs select-none">
      {/* Center/Left Tactical Header Pill */}
      <div className="flex items-center gap-3 bg-surface-100/90 border border-white/15 px-4 py-1.5 rounded-lg shadow-inner">
        <div className="flex items-center gap-2 font-bold text-slate-100 tracking-wider">
          <Shield className="w-4 h-4 text-cyan-400" />
          <span>BORDER SECURITY AI</span>
        </div>

        <span className="text-slate-600">|</span>

        <div className="hidden sm:flex items-center gap-2 text-slate-300 text-[11px]">
          <span>SECTOR: <strong className="text-slate-100">KOLKATA FRONTIER</strong></span>
          <span className="text-slate-600">|</span>
          <span>OPERATOR: <strong className="text-cyan-300 font-bold">{username}</strong></span>
        </div>

        <span className="text-slate-600">|</span>

        {/* Biometric Verified HUD Badge */}
        <div className="hidden lg:flex items-center gap-1.5 px-2 py-0.5 rounded bg-emerald-950/60 border border-emerald-500/40 text-[10px] text-emerald-300 font-bold tracking-wider">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
          <span>🔒 BIOMETRIC VERIFIED</span>
        </div>

        <span className="text-slate-600 hidden lg:inline">|</span>

        <div className="text-slate-300 text-[11px]">
          UTC: <strong className="text-emerald-400" suppressHydrationWarning>{time}</strong>
        </div>
      </div>

      {/* Right Controls: Camera Selection, Audio, Operator Profile */}
      <div className="flex items-center gap-3">
        {/* Camera Selector */}
        <div className="flex items-center gap-2">
          <Video className="w-3.5 h-3.5 text-cyan-400" />
          <select
            value={selectedCamera?.id || ""}
            onChange={(e) => selectCamera(e.target.value)}
            className="bg-surface-100 border border-white/15 text-slate-200 text-xs font-mono rounded px-2 py-1 focus:outline-none focus:border-cyan-500 cursor-pointer"
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

        {/* Operator Profile Dropdown */}
        <div className="relative" ref={profileDropdownRef}>
          <button
            onClick={() => setIsProfileOpen(!isProfileOpen)}
            className="flex items-center gap-2 px-2.5 py-1 rounded bg-slate-900/90 border border-cyan-500/30 text-slate-200 hover:border-cyan-400 transition-colors cursor-pointer"
          >
            <div className="w-5 h-5 rounded bg-cyan-500/20 border border-cyan-500/40 text-cyan-300 flex items-center justify-center font-bold text-[10px]">
              <User className="w-3 h-3" />
            </div>
            <div className="text-left hidden md:block">
              <span className="block text-[11px] font-bold text-white tracking-wider leading-none">
                {username}
              </span>
              <span className="block text-[9px] text-cyan-400 leading-none mt-0.5">
                {role}
              </span>
            </div>
            <ChevronDown className="w-3 h-3 text-slate-400 ml-0.5" />
          </button>

          {/* Dropdown Menu */}
          {isProfileOpen && (
            <div className="absolute right-0 mt-2 w-64 rounded-xl bg-[#0b1120] border border-cyan-500/30 shadow-[0_0_30px_rgba(0,0,0,0.8)] p-3 z-50 animate-in fade-in slide-in-from-top-2 duration-150">
              {/* User Header */}
              <div className="border-b border-slate-800 pb-3 mb-2">
                <div className="flex items-center gap-2 mb-1">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                  <span className="text-[10px] text-emerald-400 font-bold tracking-wider">
                    OPERATOR SESSION ACTIVE
                  </span>
                </div>
                <p className="text-sm font-bold text-white tracking-wide">{user?.username || "admin"}</p>
                <p className="text-[10px] text-slate-400">{user?.email || "admin@ibvap.local"}</p>
              </div>

              {/* Security Details */}
              <div className="space-y-1.5 mb-3 text-[11px]">
                <div className="flex items-center justify-between text-slate-400">
                  <span>Role Authorization:</span>
                  <span className="text-cyan-400 font-bold">{role}</span>
                </div>
                <div className="flex items-center justify-between text-slate-400">
                  <span>Biometric Profile:</span>
                  <span className="text-emerald-400 font-bold flex items-center gap-1">
                    <Scan className="w-3 h-3 text-emerald-400" />
                    VERIFIED (1:1)
                  </span>
                </div>
                <div className="flex items-center justify-between text-slate-400">
                  <span>MFA Protection:</span>
                  <span className="text-emerald-400 font-bold flex items-center gap-1">
                    <ShieldCheck className="w-3 h-3" />
                    ENABLED
                  </span>
                </div>
              </div>

              {/* Actions */}
              <div className="space-y-1 border-t border-slate-800 pt-2">
                <button
                  type="button"
                  onClick={() => {
                    setIsProfileOpen(false);
                    router.push("/admin/face-enrollment");
                  }}
                  className="w-full px-2.5 py-1.5 rounded hover:bg-slate-800/60 text-slate-300 hover:text-white flex items-center gap-2 text-[11px] transition-colors cursor-pointer text-left"
                >
                  <Scan className="w-3.5 h-3.5 text-cyan-400" />
                  <span>Update Biometric Profile</span>
                </button>

                <button
                  type="button"
                  onClick={() => {
                    setIsProfileOpen(false);
                    router.push("/mfa/setup");
                  }}
                  className="w-full px-2.5 py-1.5 rounded hover:bg-slate-800/60 text-slate-300 hover:text-white flex items-center gap-2 text-[11px] transition-colors cursor-pointer text-left"
                >
                  <Lock className="w-3.5 h-3.5 text-cyan-400" />
                  <span>Configure MFA Key</span>
                </button>

                <button
                  type="button"
                  onClick={handleLogout}
                  className="w-full px-2.5 py-1.5 rounded hover:bg-red-950/40 text-red-400 hover:text-red-300 flex items-center gap-2 text-[11px] transition-colors cursor-pointer text-left border border-transparent hover:border-red-500/30"
                >
                  <LogOut className="w-3.5 h-3.5" />
                  <span>End Operator Session (Logout)</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
