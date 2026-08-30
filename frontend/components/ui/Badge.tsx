import React from "react";
import { EventSeverity } from "../../types/event";
import { VerifyStatus } from "../../types/evidence";
import { CameraStatus } from "../../types/camera";

interface BadgeProps {
  children?: React.ReactNode;
  variant?: "default" | "severity" | "status" | "verify";
  severity?: EventSeverity;
  status?: CameraStatus;
  verifyStatus?: VerifyStatus;
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = "default",
  severity,
  status,
  verifyStatus,
  className = "",
}) => {
  let styles = "inline-flex items-center px-2 py-0.5 rounded text-xs font-mono font-medium tracking-wide ";

  if (severity) {
    switch (severity) {
      case "CRITICAL":
        styles += "bg-red-950/80 text-red-400 border border-red-800 animate-pulse-fast";
        break;
      case "HIGH":
        styles += "bg-red-900/60 text-red-300 border border-red-700";
        break;
      case "MEDIUM":
        styles += "bg-amber-950/70 text-amber-300 border border-amber-700";
        break;
      case "LOW":
        styles += "bg-blue-950/70 text-blue-300 border border-blue-700";
        break;
    }
    return <span className={`${styles} ${className}`}>⚠️ {children || severity}</span>;
  }

  if (status) {
    switch (status) {
      case "ACTIVE":
        styles += "bg-emerald-950/70 text-emerald-400 border border-emerald-700";
        break;
      case "OFFLINE":
        styles += "bg-slate-900/80 text-slate-400 border border-slate-700";
        break;
      case "ERROR":
        styles += "bg-red-950/80 text-red-400 border border-red-800";
        break;
    }
    return (
      <span className={`${styles} ${className}`}>
        <span className={`w-1.5 h-1.5 rounded-full mr-1.5 ${status === "ACTIVE" ? "bg-emerald-400 animate-ping" : "bg-slate-500"}`} />
        {children || status}
      </span>
    );
  }

  if (verifyStatus) {
    switch (verifyStatus) {
      case "VERIFIED":
        styles += "bg-emerald-950/90 text-emerald-300 border border-emerald-600 shadow-sm shadow-emerald-900/40";
        return <span className={`${styles} ${className}`}>🔒 VERIFIED (MATCH)</span>;
      case "MISMATCH":
      case "TAMPERED":
        styles += "bg-red-950/90 text-red-300 border border-red-600 shadow-sm shadow-red-900/40 animate-pulse";
        return <span className={`${styles} ${className}`}>🚨 TAMPERED (MISMATCH)</span>;
      case "NOT_HASHED":
        styles += "bg-amber-950/70 text-amber-300 border border-amber-700";
        return <span className={`${styles} ${className}`}>🟡 NOT HASHED</span>;
      case "PENDING":
        styles += "bg-amber-950/70 text-amber-300 border border-amber-700";
        return <span className={`${styles} ${className}`}>⏳ VERIFYING...</span>;
      default:
        styles += "bg-slate-800 text-slate-400 border border-slate-700";
        return <span className={`${styles} ${className}`}>UNVERIFIED</span>;
    }
  }

  return <span className={`${styles} bg-surface-100 text-slate-300 border border-surface-border ${className}`}>{children}</span>;
};
