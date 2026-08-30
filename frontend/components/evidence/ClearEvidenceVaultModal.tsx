"use client";

import React, { useState, useEffect, useRef } from "react";
import { AlertTriangle, Trash2, X, ShieldAlert, FileX } from "lucide-react";

interface ClearEvidenceVaultModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  isClearing?: boolean;
  recordCount?: number;
}

export const ClearEvidenceVaultModal: React.FC<ClearEvidenceVaultModalProps> = ({
  isOpen,
  onClose,
  onConfirm,
  isClearing = false,
  recordCount = 0,
}) => {
  const [confirmationInput, setConfirmationInput] = useState("");
  const inputRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    if (isOpen) {
      setConfirmationInput("");
      setTimeout(() => {
        inputRef.current?.focus();
      }, 100);
      document.body.style.overflow = "hidden";
    }
    return () => {
      document.body.style.overflow = "unset";
    };
  }, [isOpen]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && !isClearing) {
        onClose();
      }
    };
    if (isOpen) {
      window.addEventListener("keydown", handleKeyDown);
    }
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [isOpen, onClose, isClearing]);

  if (!isOpen) return null;

  const isConfirmed = confirmationInput.trim() === "CLEAR";

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (isConfirmed && !isClearing) {
      onConfirm();
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/85 backdrop-blur-md transition-opacity animate-in fade-in"
        onClick={!isClearing ? onClose : undefined}
      />

      {/* Dialog Box */}
      <div className="relative z-10 w-full max-w-lg bg-[#0b1120] border-2 border-red-800/80 rounded-2xl shadow-[0_0_60px_rgba(239,68,68,0.25)] overflow-hidden flex flex-col font-sans select-none animate-in zoom-in-95 duration-200">
        
        {/* Header HUD Bar */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-red-900/50 bg-red-950/40">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-red-950 border border-red-500/60 text-red-400 shadow-[0_0_15px_rgba(239,68,68,0.3)]">
              <ShieldAlert className="w-5 h-5 animate-pulse" />
            </div>
            <div>
              <h2 className="text-sm font-bold tracking-wider text-red-200 font-mono uppercase">
                Clear Evidence Vault?
              </h2>
              <p className="text-[11px] text-red-300/80 font-mono">
                IRREVERSIBLE CRYPTOGRAPHIC PURGE
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            disabled={isClearing}
            className="text-slate-400 hover:text-slate-200 p-1.5 rounded-lg hover:bg-slate-800 transition disabled:opacity-50 cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-5">
          
          {/* Main Warning Box */}
          <div className="p-4 rounded-xl bg-red-950/30 border border-red-900/50 flex items-start gap-3.5">
            <AlertTriangle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
            <div className="space-y-1.5 text-xs">
              <p className="font-semibold text-slate-200">
                Warning: Permanent Deletion
              </p>
              <p className="text-red-300 leading-relaxed font-mono">
                This action will permanently remove all captured evidence, snapshots, metadata, and associated integrity records.
              </p>
            </div>
          </div>

          {/* Record Count Badge */}
          <div className="p-3 rounded-xl bg-slate-900/70 border border-slate-800 flex items-center justify-between text-xs font-mono">
            <span className="text-slate-400 flex items-center gap-2">
              <FileX className="w-4 h-4 text-slate-500" />
              Evidence Records Targeted:
            </span>
            <span className="px-2.5 py-0.5 rounded-md bg-red-950 border border-red-800 text-red-300 font-bold">
              {recordCount} {recordCount === 1 ? "Record" : "Records"}
            </span>
          </div>

          {/* Type CLEAR input confirmation */}
          <div className="space-y-2 font-mono">
            <label className="text-xs text-slate-300 block">
              Type <strong className="text-red-400 font-bold bg-red-950/80 px-1.5 py-0.5 rounded border border-red-800">CLEAR</strong> below to confirm vault deletion:
            </label>
            <input
              ref={inputRef}
              type="text"
              value={confirmationInput}
              onChange={(e) => setConfirmationInput(e.target.value)}
              placeholder="Type CLEAR to enable"
              disabled={isClearing}
              className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-700 focus:border-red-500 focus:ring-1 focus:ring-red-500 text-slate-100 text-sm font-mono tracking-wider outline-none transition disabled:opacity-50"
            />
          </div>

          {/* Action Buttons */}
          <div className="pt-3 border-t border-slate-800/80 flex items-center justify-end gap-3 font-mono">
            <button
              type="button"
              onClick={onClose}
              disabled={isClearing}
              className="px-4 py-2.5 rounded-xl bg-slate-800/80 hover:bg-slate-700 border border-slate-700 text-slate-300 hover:text-white text-xs font-semibold uppercase tracking-wider transition cursor-pointer disabled:opacity-50"
            >
              CANCEL
            </button>

            <button
              type="submit"
              disabled={!isConfirmed || isClearing}
              className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-red-700 via-red-600 to-rose-700 hover:from-red-600 hover:to-rose-600 disabled:opacity-35 disabled:cursor-not-allowed text-white text-xs font-bold font-mono tracking-wider uppercase border border-red-500/70 shadow-[0_0_25px_rgba(239,68,68,0.4)] flex items-center gap-2 transition cursor-pointer"
            >
              {isClearing ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span>PURGING VAULT...</span>
                </>
              ) : (
                <>
                  <Trash2 className="w-4 h-4" />
                  <span>CLEAR ALL EVIDENCE</span>
                </>
              )}
            </button>
          </div>

        </form>
      </div>
    </div>
  );
};
