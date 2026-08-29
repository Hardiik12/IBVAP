"use client";

import React, { useState, useEffect } from "react";
import { EvidenceRecord } from "../../types/evidence";
import { evidenceService } from "../../services/evidenceService";
import { useAlerts } from "../../hooks/useAlerts";
import { Badge } from "../../components/ui/Badge";
import { Card } from "../../components/ui/Card";
import { formatDate, truncateHash } from "../../utils/formatters";
import {
  FileCheck2,
  KeyRound,
  FileSearch,
  Lock,
  Camera,
  RefreshCw,
} from "lucide-react";

export default function EvidencePage() {
  const { openEvidenceModal } = useAlerts();
  const [evidenceList, setEvidenceList] = useState<EvidenceRecord[]>([]);
  const [isLoading, setIsLoading] = useState(true);

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

  return (
    <div className="space-y-6 animate-fade-in max-w-6xl">
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
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-surface-100 hover:bg-surface-50 border border-surface-border text-xs font-mono text-slate-300 transition"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? "animate-spin" : ""}`} />
            <span>Refresh Vault</span>
          </button>

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

      {/* Evidence Cards Grid */}
      {isLoading ? (
        <div className="h-48 flex items-center justify-center font-mono text-xs text-slate-400 animate-pulse">
          Loading cryptographic evidence records...
        </div>
      ) : evidenceList.length === 0 ? (
        <div className="bg-surface-200/60 border border-surface-border rounded-xl p-8 text-center space-y-3 font-mono">
          <Camera className="w-8 h-8 text-slate-500 mx-auto" />
          <div className="text-sm text-slate-200 font-bold">No Evidence Snapshots Captured Yet</div>
          <div className="text-xs text-slate-400 max-w-md mx-auto">
            Open the main Surveillance Monitor on the Dashboard. Move into the virtual restricted zone to automatically capture real webcam evidence frames and generate cryptographic hashes.
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
    </div>
  );
}
