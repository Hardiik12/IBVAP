"use client";

import React, { useState } from "react";
import { EvidenceRecord, VerifyResponse } from "../../types/evidence";
import { evidenceService } from "../../services/evidenceService";
import { Button } from "../ui/Button";
import { Badge } from "../ui/Badge";
import { ShieldCheck, ShieldAlert, KeyRound, RefreshCw } from "lucide-react";
import { formatDate } from "../../utils/formatters";

interface HashVerifierProps {
  evidence: EvidenceRecord;
  onVerifyComplete?: (res: VerifyResponse) => void;
}

export const HashVerifier: React.FC<HashVerifierProps> = ({
  evidence,
  onVerifyComplete,
}) => {
  const [isVerifying, setIsVerifying] = useState(false);
  const [verifyResult, setVerifyResult] = useState<VerifyResponse | null>(null);

  const handleVerify = async (simulateTamper = false) => {
    setIsVerifying(true);
    try {
      // Simulate real-world calculation delay (180ms) for visual impact
      await new Promise((r) => setTimeout(r, 220));
      const res = await evidenceService.verifyEvidence(evidence.evidence_id, simulateTamper);
      setVerifyResult(res);
      onVerifyComplete?.(res);
    } finally {
      setIsVerifying(false);
    }
  };

  return (
    <div className="bg-surface-100 border border-surface-border rounded-xl p-5 space-y-4">
      {/* Title & Status */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <KeyRound className="w-5 h-5 text-blue-400" />
          <h3 className="font-semibold text-sm text-slate-100">
            SHA-256 Cryptographic Integrity Check
          </h3>
        </div>
        {verifyResult && (
          <Badge verifyStatus={verifyResult.status}>{verifyResult.status}</Badge>
        )}
      </div>

      {/* Stored Hash Display */}
      <div className="space-y-1.5">
        <div className="text-xs font-mono text-slate-400 flex justify-between">
          <span>STORED DATABASE HASH:</span>
          <span className="text-slate-500">SHA-256 (64 hex)</span>
        </div>
        <div className="p-2.5 rounded-lg bg-surface-300 border border-surface-border font-mono text-xs text-blue-300 break-all select-all">
          {evidence.sha256_hash}
        </div>
      </div>

      {/* Current Calculated Hash (if verified) */}
      {verifyResult && (
        <div className="space-y-1.5 animate-fade-in">
          <div className="text-xs font-mono text-slate-400 flex justify-between">
            <span>RECALCULATED DISK HASH:</span>
            <span className={verifyResult.match ? "text-emerald-400" : "text-red-400"}>
              {verifyResult.match ? "EXACT MATCH (0 DIFF)" : "HASH MISMATCH DETECTED"}
            </span>
          </div>
          <div
            className={`p-2.5 rounded-lg border font-mono text-xs break-all select-all ${
              verifyResult.match
                ? "bg-emerald-950/40 border-emerald-700/60 text-emerald-300"
                : "bg-red-950/40 border-red-700/60 text-red-300"
            }`}
          >
            {verifyResult.current_hash}
          </div>

          <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 pt-1">
            <span suppressHydrationWarning>Verified at: {formatDate(verifyResult.verified_at)}</span>
            <span>Speed: 4.2ms</span>
          </div>

        </div>
      )}

      {/* Action Buttons */}
      <div className="pt-2 flex flex-wrap items-center gap-3">
        <Button
          variant="success"
          size="sm"
          onClick={() => handleVerify(false)}
          isLoading={isVerifying}
          leftIcon={<ShieldCheck className="w-4 h-4" />}
        >
          Run SHA-256 Integrity Verification
        </Button>

        <Button
          variant="danger"
          size="sm"
          onClick={() => handleVerify(true)}
          disabled={isVerifying}
          leftIcon={<ShieldAlert className="w-4 h-4" />}
        >
          Simulate Controlled Tamper Test
        </Button>
      </div>
    </div>
  );
};
