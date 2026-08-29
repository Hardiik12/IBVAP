"use client";

import React, { useEffect, useState } from "react";
import { Modal } from "../ui/Modal";
import { HashVerifier } from "./HashVerifier";
import { EvidenceRecord } from "../../types/evidence";
import { evidenceService } from "../../services/evidenceService";
import { useAlerts } from "../../hooks/useAlerts";
import { FileCheck, Camera, Clock, FileCode, Shield } from "lucide-react";
import { formatDate } from "../../utils/formatters";

export const EvidenceModal: React.FC = () => {
  const { activeEvidenceModalId, closeEvidenceModal } = useAlerts();
  const [evidence, setEvidence] = useState<EvidenceRecord | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (!activeEvidenceModalId) {
      setEvidence(null);
      return;
    }

    const load = async () => {
      setIsLoading(true);
      try {
        const data = await evidenceService.getEvidence(activeEvidenceModalId);
        setEvidence(data);
      } finally {
        setIsLoading(false);
      }
    };
    load();
  }, [activeEvidenceModalId]);

  if (!activeEvidenceModalId) return null;

  return (
    <Modal
      isOpen={!!activeEvidenceModalId}
      onClose={closeEvidenceModal}
      maxWidth="4xl"
      title={
        <div className="flex items-center gap-2">
          <Shield className="w-5 h-5 text-blue-400" />
          <span>Evidence Chain of Custody & Verification</span>
          <span className="text-xs font-mono px-2 py-0.5 rounded bg-surface-100 text-blue-300 border border-surface-border">
            {activeEvidenceModalId}
          </span>
        </div>
      }
    >
      {isLoading || !evidence ? (
        <div className="h-64 flex items-center justify-center font-mono text-xs text-slate-400 animate-pulse">
          Loading evidence payload...
        </div>
      ) : (
        <div className="space-y-6">
          {/* Main Grid: Snapshot on Left, Metadata on Right */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Snapshot Image Container */}
            <div className="space-y-2">
              <div className="text-xs font-mono text-slate-400 flex items-center gap-1.5">
                <Camera className="w-3.5 h-3.5 text-blue-400" />
                <span>HIGH-RESOLUTION EVENT SNAPSHOT:</span>
              </div>
              <div className="relative aspect-video rounded-lg overflow-hidden border border-slate-700 bg-black flex items-center justify-center">
                {/* Fallback image */}
                <img
                  src={evidence.image_url}
                  alt={`Evidence ${evidence.evidence_id}`}
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    // Fallback to stylized SVG placeholder if image path is not yet present on disk
                    (e.target as HTMLImageElement).src =
                      "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='640' height='360' viewBox='0 0 640 360'><rect width='640' height='360' fill='%230f172a'/><text x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' fill='%2364748b' font-family='monospace' font-size='14'>IBVAP EVIDENCE SNAPSHOT</text></svg>";
                  }}
                />
                <div className="absolute top-2 left-2 px-2 py-0.5 rounded bg-black/80 text-[10px] font-mono text-emerald-400 border border-slate-700">
                  AUTO-CAPTURED UPON INTRUSION
                </div>
              </div>
            </div>

            {/* Metadata & Audit Sidebar */}
            <div className="bg-surface-100 border border-surface-border rounded-lg p-4 space-y-3.5 text-xs font-mono">
              <div className="text-slate-300 font-semibold border-b border-surface-border pb-2 flex items-center gap-1.5">
                <FileCode className="w-4 h-4 text-blue-400" />
                <span>EVENT METADATA</span>
              </div>

              <div className="space-y-2 text-slate-400">
                <div className="flex justify-between">
                  <span>EVIDENCE ID:</span>
                  <span className="text-slate-200 font-bold">{evidence.evidence_id}</span>
                </div>
                <div className="flex justify-between">
                  <span>ASSOCIATED EVENT:</span>
                  <span className="text-blue-400">{evidence.event_id}</span>
                </div>
                <div className="flex justify-between">
                  <span>CAMERA SOURCE:</span>
                  <span className="text-slate-200">{evidence.camera_id || "cam-01"}</span>
                </div>
                <div className="flex justify-between">
                  <span>CAPTURED TIMESTAMP:</span>
                  <span className="text-slate-200" suppressHydrationWarning>{formatDate(evidence.captured_at)}</span>
                </div>

                <div className="flex justify-between">
                  <span>STORAGE PATH:</span>
                  <span className="text-slate-400 text-[11px] truncate max-w-[180px]">
                    {evidence.file_path}
                  </span>
                </div>
              </div>

              <div className="p-2.5 rounded bg-surface-200 border border-surface-border/80 text-[11px] text-slate-400 leading-relaxed">
                ℹ️ Forensic integrity is guaranteed by computing SHA-256 binary hash immediately upon frame capture. Any disk modification alters the hash digest.
              </div>
            </div>
          </div>

          {/* Cryptographic Hash Verification Widget */}
          <HashVerifier evidence={evidence} />
        </div>
      )}
    </Modal>
  );
};
