"use client";

import React, { useEffect } from "react";
import { AlertTriangle, Trash2, X, ShieldAlert } from "lucide-react";

interface ClearLogsModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  isClearing?: boolean;
}

export const ClearLogsModal: React.FC<ClearLogsModalProps> = ({
  isOpen,
  onClose,
  onConfirm,
  isClearing = false,
}) => {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && !isClearing) onClose();
    };
    if (isOpen) {
      document.body.style.overflow = "hidden";
      window.addEventListener("keydown", handleKeyDown);
    }
    return () => {
      document.body.style.overflow = "unset";
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [isOpen, onClose, isClearing]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/80 backdrop-blur-sm transition-opacity animate-in fade-in"
        onClick={!isClearing ? onClose : undefined}
      />

      {/* Dialog Box */}
      <div className="relative z-10 w-full max-w-md bg-[#0b1120] border border-red-900/60 rounded-2xl shadow-[0_0_50px_rgba(239,68,68,0.2)] overflow-hidden flex flex-col font-sans select-none animate-in zoom-in-95 duration-200">
        
        {/* Top Header Bar */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-red-900/40 bg-red-950/30">
          <div className="flex items-center gap-2.5">
            <div className="p-1.5 rounded-lg bg-red-950/80 border border-red-500/50 text-red-400">
              <ShieldAlert className="w-4 h-4" />
            </div>
            <h2 className="text-sm font-bold tracking-wider text-red-300 font-mono uppercase">
              Clear Audit Logs?
            </h2>
          </div>
          <button
            onClick={onClose}
            disabled={isClearing}
            className="text-slate-400 hover:text-slate-200 p-1.5 rounded-lg hover:bg-slate-800 transition disabled:opacity-50 cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 space-y-4">
          <div className="flex items-start gap-3.5 p-3.5 rounded-xl bg-red-950/20 border border-red-900/30">
            <AlertTriangle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
            <div className="space-y-1">
              <p className="text-xs font-semibold text-slate-200">
                Permanent Data Destruction
              </p>
              <p className="text-xs text-red-300/90 font-mono">
                This action will permanently remove all audit log entries.
              </p>
            </div>
          </div>

          <p className="text-xs text-slate-400">
            Historical forensic audit records and event transition timelines will be cleared from the system database. This operation cannot be undone.
          </p>
        </div>

        {/* Modal Footer Actions */}
        <div className="px-6 py-4 border-t border-red-900/30 bg-slate-950/60 flex items-center justify-end gap-3">
          <button
            type="button"
            onClick={onClose}
            disabled={isClearing}
            className="px-4 py-2 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700 text-slate-300 hover:text-white text-xs font-semibold transition cursor-pointer disabled:opacity-50"
          >
            Cancel
          </button>

          <button
            type="button"
            onClick={onConfirm}
            disabled={isClearing}
            className="px-5 py-2 rounded-xl bg-gradient-to-r from-red-700 to-rose-700 hover:from-red-600 hover:to-rose-600 text-white text-xs font-bold font-mono tracking-wider uppercase border border-red-500/60 shadow-[0_0_20px_rgba(239,68,68,0.4)] flex items-center gap-2 transition cursor-pointer disabled:opacity-50"
          >
            {isClearing ? (
              <>
                <div className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                <span>Clearing...</span>
              </>
            ) : (
              <>
                <Trash2 className="w-3.5 h-3.5" />
                <span>Clear All Logs</span>
              </>
            )}
          </button>
        </div>

      </div>
    </div>
  );
};
