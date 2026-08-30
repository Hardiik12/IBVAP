"use client";

import React, { useState, useEffect } from "react";
import { EvidenceRecord } from "../../types/evidence";
import { evidenceService } from "../../services/evidenceService";
import { useAlerts } from "../../hooks/useAlerts";
import { useAuth } from "../../context/AuthContext";
import { Badge } from "../../components/ui/Badge";
import { Card } from "../../components/ui/Card";
import { ClearEvidenceVaultModal } from "../../components/evidence/ClearEvidenceVaultModal";
import { formatDate, truncateHash } from "../../utils/formatters";
import {
  FileCheck2,
  KeyRound,
  FileSearch,
  Lock,
  Camera,
  RefreshCw,
  Trash2,
  CheckCircle2,
  AlertCircle,
  FolderX,
} from "lucide-react";

export default function EvidencePage() {
  const { user } = useAuth();
  const { openEvidenceModal } = useAlerts();
  const [evidenceList, setEvidenceList] = useState<EvidenceRecord[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Modal and toast states
  const [isClearModalOpen, setIsClearModalOpen] = useState(false);
  const [isClearing, setIsClearing] = useState(false);
  const [toastMessage, setToastMessage] = useState<{
    text: string;
    type: "success" | "error";
  } | null>(null);

  const canClearVault = user?.role === "ADMINISTRATOR" || user?.role === "OPERATOR";

  const loadEvidence = async () => {
    setIsLoading(true);
    try {
      const data = await evidenceService.getAllEvidence();
      setEvidenceList(data);
    } catch (err) {
      console.error("Failed to load real evidence records:", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadEvidence();
  }, []);

  // Auto-dismiss toast notification
  useEffect(() => {
    if (toastMessage) {
      const timer = setTimeout(() => {
        setToastMessage(null);
      }, 4000);
      return () => clearTimeout(timer);
    }
  }, [toastMessage]);

  const handleClearEvidenceVaultConfirm = async () => {
    if (!canClearVault) {
      setToastMessage({
        text: "ACCESS DENIED: Insufficient permissions to purge evidence vault.",
        type: "error",
      });
      setIsClearModalOpen(false);
      return;
    }

    setIsClearing(true);
    try {
      await evidenceService.clearEvidenceVault();
      // Immediately reset local state to render empty state
      setEvidenceList([]);
      setIsClearModalOpen(false);
      setToastMessage({
        text: "EVIDENCE VAULT CLEARED SUCCESSFULLY",
        type: "success",
      });
    } catch (err: any) {
      console.error("Failed to clear evidence vault:", err);
      const detail =
        err.response?.data?.detail ||
        err.message ||
        "Failed to clear evidence vault.";
      setToastMessage({
        text: `PURGE FAILED: ${detail}`,
        type: "error",
      });
      setIsClearModalOpen(false);
    } finally {
      setIsClearing(false);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in max-w-6xl relative">
      {/* Temporary Toast Notification */}
      {toastMessage && (
        <div className="fixed top-6 right-6 z-50 animate-in slide-in-from-top-4 duration-300">
          <div
            className={`flex items-center gap-3 px-5 py-3.5 rounded-xl border font-mono text-xs shadow-2xl backdrop-blur-xl ${
              toastMessage.type === "success"
                ? "bg-emerald-950/90 border-emerald-500/60 text-emerald-300 shadow-[0_0_30px_rgba(16,185,129,0.3)]"
                : "bg-red-950/90 border-red-500/60 text-red-300 shadow-[0_0_30px_rgba(239,68,68,0.3)]"
            }`}
          >
            {toastMessage.type === "success" ? (
              <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
            ) : (
              <AlertCircle className="w-5 h-5 text-red-400 shrink-0" />
            )}
            <span className="font-semibold uppercase tracking-wider">
              {toastMessage.text}
            </span>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-surface-border pb-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <FileCheck2 className="w-5 h-5 text-blue-400" />
            <span>Cryptographic Evidence Vault</span>
          </h1>
          <p className="text-xs font-mono text-slate-400 mt-1">
            Real-time webcam evidence capture & SHA-256 binary hash integrity verification
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={loadEvidence}
            disabled={isLoading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-surface-100 hover:bg-surface-50 border border-surface-border text-xs font-mono text-slate-300 transition cursor-pointer"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? "animate-spin" : ""}`} />
            <span>Refresh Vault</span>
          </button>

          {/* CLEAR EVIDENCE VAULT Action Button */}
          {canClearVault && (
            <button
              onClick={() => setIsClearModalOpen(true)}
              disabled={evidenceList.length === 0}
              title={
                evidenceList.length === 0
                  ? "No evidence to purge"
                  : "Permanently delete all stored evidence files and hash records"
              }
              className="flex items-center gap-2 px-3.5 py-1.5 rounded-lg bg-red-950/40 hover:bg-red-900/60 disabled:opacity-40 disabled:cursor-not-allowed border border-red-800/80 hover:border-red-600 text-red-300 hover:text-red-100 text-xs font-mono font-medium transition cursor-pointer shadow-[0_0_15px_rgba(239,68,68,0.2)]"
            >
              <Trash2 className="w-3.5 h-3.5 text-red-400" />
              <span>CLEAR EVIDENCE VAULT</span>
            </button>
          )}

          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-blue-950/40 border border-blue-800/60 text-xs font-mono text-blue-300">
            <Lock className="w-3.5 h-3.5" />
            <span>ALGORITHM: SHA-256</span>
          </div>
        </div>
      </div>

      {/* Forensic Architecture Note */}
      <div className="bg-surface-200 border border-surface-border rounded-xl p-4 flex items-start gap-3">
        <KeyRound className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
        <div className="text-xs text-slate-300 leading-relaxed font-sans">
          <strong className="text-slate-100 font-mono">Real-Time Chain of Custody:</strong> When an intrusion is triggered via the live webcam, IBVAP writes the exact raw video frame to disk and calculates its 64-character SHA-256 cryptographic hash. Clicking <strong>Inspect & Verify</strong> executes an on-demand verification of the physical image on disk to guarantee zero tampering.
        </div>
      </div>

      {/* Evidence Cards Grid / Empty State */}
      {isLoading ? (
        <div className="h-48 flex items-center justify-center font-mono text-xs text-slate-400 animate-pulse">
          Loading cryptographic evidence records...
        </div>
      ) : evidenceList.length === 0 ? (
        <div className="bg-surface-200/60 border border-surface-border rounded-xl p-12 text-center space-y-3 font-mono flex flex-col items-center justify-center">
          <div className="p-3 rounded-2xl bg-surface-100 border border-surface-border text-slate-500 mb-1">
            <FolderX className="w-8 h-8 text-slate-400" />
          </div>
          <div className="text-base text-slate-200 font-bold uppercase tracking-wider">
            NO EVIDENCE RECORDS AVAILABLE
          </div>
          <div className="text-xs text-slate-400 max-w-md mx-auto leading-relaxed">
            All historical cryptographic evidence files and SHA-256 integrity logs have been purged. Real-time webcam intrusions will automatically capture fresh evidence snapshots.
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {evidenceList.map((item) => (
            <Card
              key={item.evidence_id}
              className="group hover:border-slate-600 transition-all cursor-pointer bg-surface-200 shadow-md"
              onClick={() => openEvidenceModal(item.evidence_id)}
            >
              {/* Real Snapshot Thumbnail */}
              <div className="relative aspect-video rounded-md overflow-hidden bg-black mb-3 border border-slate-700">
                <img
                  src={item.image_url}
                  alt={item.evidence_id}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  onError={(e) => {
                    (e.target as HTMLImageElement).src =
                      "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='400' height='225' viewBox='0 0 400 225'><rect width='400' height='225' fill='%230f172a'/><text x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' fill='%2364748b' font-family='monospace' font-size='12'>EVIDENCE SNAPSHOT</text></svg>";
                  }}
                />
                <div className="absolute top-2 left-2">
                  <Badge verifyStatus={item.verified_status}>{item.verified_status}</Badge>
                </div>
              </div>

              {/* Evidence Metadata */}
              <div className="space-y-2 text-xs font-mono">
                <div className="flex items-center justify-between text-slate-200 font-bold">
                  <span>{item.evidence_id.substring(0, 16)}...</span>
                  <span className="text-blue-400 font-normal">{item.event_id.substring(0, 12)}...</span>
                </div>

                <div className="p-2 rounded bg-surface-300 border border-surface-border text-[11px] text-slate-400 break-all select-all">
                  <span className="text-slate-500 block text-[9px]">REAL SHA-256 DIGEST:</span>
                  {truncateHash(item.sha256_hash, 12, 12)}
                </div>

                <div className="flex items-center justify-between text-[11px] text-slate-400 pt-1">
                  <span suppressHydrationWarning>{formatDate(item.captured_at)}</span>
                  <span className="text-blue-400 group-hover:underline flex items-center gap-1 font-bold">
                    <FileSearch className="w-3 h-3" />
                    Inspect & Verify
                  </span>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Strong Typed Confirmation Modal */}
      <ClearEvidenceVaultModal
        isOpen={isClearModalOpen}
        onClose={() => setIsClearModalOpen(false)}
        onConfirm={handleClearEvidenceVaultConfirm}
        isClearing={isClearing}
        recordCount={evidenceList.length}
      />
    </div>
  );
}
