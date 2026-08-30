"use client";

import React, { useState } from "react";
import { EvidenceRecord, VerifyResponse } from "../../types/evidence";
import { evidenceService } from "../../services/evidenceService";
import { Button } from "../ui/Button";
import { Badge } from "../ui/Badge";
import { ShieldCheck, ShieldAlert, KeyRound, AlertTriangle, RefreshCw } from "lucide-react";
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
  const [isHashing, setIsHashing] = useState(false);
  const [currentHash, setCurrentHash] = useState<string | null>(evidence.sha256_hash);
  const [verifyResult, setVerifyResult] = useState<VerifyResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const isNotHashed = !currentHash || currentHash === "NOT_HASHED" || currentHash === "UNAVAILABLE";

  const handleGenerateHash = async () => {
    setIsHashing(true);
    setError(null);
    try {
      const res = await evidenceService.generateHash(evidence.evidence_id);
      setCurrentHash(res.sha256_hash);
    } catch (err: any) {
      setError(err?.message || "Failed to generate server-side SHA-256 hash.");
    } finally {
      setIsHashing(false);
    }
  };

  const handleVerify = async () => {
    setIsVerifying(true);
    setError(null);
    try {
      const res = await evidenceService.verifyEvidence(evidence.evidence_id);
      setVerifyResult(res);
      if (res.stored_hash) setCurrentHash(res.stored_hash);
      onVerifyComplete?.(res);
    } catch (err: any) {
      setError(err?.message || "Failed to execute backend hash verification.");
    } finally {
      setIsVerifying(false);
    }
  };

  return (
    <div className="bg-surface-100 border border-surface-border rounded-xl p-5 space-y-4 font-mono">
      {/* Title & Status */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <KeyRound className="w-5 h-5 text-blue-400" />
          <h3 className="font-semibold text-sm text-slate-100 font-sans">
            SHA-256 Cryptographic Integrity Check
          </h3>
        </div>
        {verifyResult ? (
          <Badge verifyStatus={verifyResult.status as any}>{verifyResult.status}</Badge>
        ) : isNotHashed ? (
          <Badge verifyStatus="PENDING">NOT_HASHED</Badge>
        ) : (
          <Badge verifyStatus="UNKNOWN">HASHED</Badge>
        )}
      </div>

      {error && (
        <div className="p-3 rounded-lg bg-red-950/50 border border-red-800/60 text-xs text-red-300 flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-red-400 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Stored Hash Display */}
      <div className="space-y-1.5">
        <div className="text-xs text-slate-400 flex justify-between">
          <span>STORED DATABASE HASH:</span>
          <span className="text-slate-500">SHA-256 (64 HEX DIGEST)</span>
        </div>
        <div className={`p-2.5 rounded-lg border text-xs break-all select-all ${
          isNotHashed ? "bg-amber-950/30 border-amber-800/50 text-amber-300" : "bg-surface-300 border-surface-border text-blue-300"
        }`}>
          {isNotHashed ? "NOT_HASHED (Pending initial hash digest generation)" : currentHash}
        </div>
      </div>

      {/* Current Calculated Hash (if verified) */}
      {verifyResult && (
        <div className="space-y-1.5 animate-fade-in">
          <div className="text-xs text-slate-400 flex justify-between">
            <span>RECALCULATED DISK HASH:</span>
            <span className={verifyResult.status === "VERIFIED" ? "text-emerald-400 font-bold" : "text-red-400 font-bold"}>
              {verifyResult.status === "VERIFIED" ? "EXACT MATCH (0 DIFF - UNTAMPERED)" : "HASH MISMATCH (TAMPER DETECTED)"}
            </span>
          </div>
          <div
            className={`p-2.5 rounded-lg border text-xs break-all select-all ${
              verifyResult.status === "VERIFIED"
                ? "bg-emerald-950/40 border-emerald-700/60 text-emerald-300"
                : "bg-red-950/40 border-red-700/60 text-red-300"
            }`}
          >
            {verifyResult.current_hash || currentHash}
          </div>

          <div className="flex items-center justify-between text-[11px] text-slate-400 pt-1">
            <span suppressHydrationWarning>Verified at: {formatDate(verifyResult.verified_at || new Date().toISOString())}</span>
            <span className={verifyResult.status === "VERIFIED" ? "text-emerald-400 font-bold" : "text-red-400 font-bold"}>
              STATUS: {verifyResult.status}
            </span>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="pt-2 flex flex-wrap items-center gap-3">
        {isNotHashed ? (
          <Button
            variant="secondary"
            size="sm"
            onClick={handleGenerateHash}
            isLoading={isHashing}
            leftIcon={<RefreshCw className="w-4 h-4" />}
            className="w-full sm:w-auto"
          >
            {isHashing ? "Generating Hash..." : "Generate Server-Side SHA-256 Hash"}
          </Button>
        ) : (
          <Button
            variant={verifyResult?.status === "MISMATCH" ? "danger" : "success"}
            size="sm"
            onClick={handleVerify}
            isLoading={isVerifying}
            leftIcon={verifyResult?.status === "MISMATCH" ? <ShieldAlert className="w-4 h-4" /> : <ShieldCheck className="w-4 h-4" />}
            className="w-full sm:w-auto"
          >
            {isVerifying ? "Verifying Disk Binary..." : "Execute Authoritative SHA-256 Verification"}
          </Button>
        )}
      </div>
    </div>
  );
};
