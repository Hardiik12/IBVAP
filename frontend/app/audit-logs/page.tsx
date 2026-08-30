"use client";

import React, { useState, useEffect, useCallback } from "react";
import { useAuth } from "../../context/AuthContext";
import { auditService } from "../../services/auditService";
import { AuditLogRecord } from "../../types/audit";
import { Card } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";
import { formatDate } from "../../utils/formatters";
import {
  ListOrdered,
  ShieldCheck,
  RefreshCw,
  Search,
  Filter,
  Lock,
  User,
  Activity,
  AlertTriangle,
} from "lucide-react";

export default function AuditLogsPage() {
  const { user, hasRole } = useAuth();
  const [logs, setLogs] = useState<AuditLogRecord[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionFilter, setActionFilter] = useState<string>("");

  const isAuthorized = hasRole(["ADMINISTRATOR", "AUDITOR"]);

  const loadAuditLogs = useCallback(async () => {
    if (!isAuthorized) {
      setIsLoading(false);
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const data = await auditService.getAuditLogs({
        action: actionFilter || undefined,
        limit: 50,
      });
      setLogs(data);
    } catch (err: any) {
      setError(err?.message || "Failed to fetch audit log trail.");
    } finally {
      setIsLoading(false);
    }
  }, [actionFilter, isAuthorized]);

  useEffect(() => {
    loadAuditLogs();
  }, [loadAuditLogs]);

  const getActionBadgeClass = (action: string) => {
    if (action.includes("LOGIN_SUCCESS")) return "bg-emerald-950/70 text-emerald-400 border-emerald-800";
    if (action.includes("LOGIN_FAILURE") || action.includes("TAMPER")) return "bg-red-950/80 text-red-400 border-red-800 animate-pulse";
    if (action.includes("VERIFY") || action.includes("EVIDENCE")) return "bg-blue-950/70 text-blue-400 border-blue-800";
    if (action.includes("ALERT") || action.includes("EVENT")) return "bg-amber-950/70 text-amber-300 border-amber-800";
    return "bg-surface-300 text-slate-300 border-surface-border";
  };

  if (!isAuthorized) {
    return (
      <div className="space-y-6 animate-fade-in max-w-4xl font-mono">
        <div className="bg-surface-200 border border-red-800/60 rounded-xl p-8 text-center space-y-4">
          <div className="w-12 h-12 rounded-full bg-red-950/80 border border-red-700/80 flex items-center justify-center text-red-400 mx-auto">
            <Lock className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-base font-bold text-slate-100">ACCESS RESTRICTED — RBAC GATED</h2>
            <p className="text-xs text-slate-400 mt-1 font-sans max-w-md mx-auto">
              System Audit Logs are restricted to <strong>ADMINISTRATOR</strong> and <strong>AUDITOR</strong> roles in compliance with forensic chain-of-custody protocols.
            </p>
          </div>
          <div className="text-[11px] text-slate-500 font-mono">
            Current Authenticated Role: <span className="text-amber-400 font-bold">{user?.role || "UNKNOWN"}</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in max-w-6xl font-mono">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-surface-border pb-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <ListOrdered className="w-5 h-5 text-blue-400" />
            <span>Forensic Security Audit Trail</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1 font-sans">
            Immutable system audit logs tracking authentication, event creation, alert resolutions, and cryptographic verification
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant="outline"
            onClick={loadAuditLogs}
            isLoading={isLoading}
            leftIcon={<RefreshCw className="w-3.5 h-3.5" />}
          >
            Refresh Logs
          </Button>
        </div>
      </div>

      {/* Security Compliance Banner */}
      <div className="bg-surface-200 border border-surface-border rounded-xl p-4 flex items-start gap-3">
        <Lock className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
        <div className="text-xs text-slate-300 leading-relaxed font-sans">
          <strong className="text-slate-100 font-mono">Forensic Accountability:</strong> All critical state mutations across IBVAP are recorded immutably in the database with timestamps and actor context for regulatory compliance and chain-of-custody verification.
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-3 bg-surface-200/80 border border-surface-border p-3 rounded-lg text-xs">
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-slate-400" />
          <span className="text-slate-400">ACTION FILTER:</span>
          <select
            value={actionFilter}
            onChange={(e) => setActionFilter(e.target.value)}
            className="bg-surface-100 border border-white/15 text-slate-200 text-xs font-mono rounded px-2.5 py-1 focus:outline-none focus:border-blue-500 cursor-pointer"
          >
            <option value="">ALL ACTIONS</option>
            <option value="LOGIN_SUCCESS">LOGIN_SUCCESS</option>
            <option value="LOGIN_FAILURE">LOGIN_FAILURE</option>
            <option value="EVENT_CREATED">EVENT_CREATED</option>
            <option value="ALERT_ACKNOWLEDGED">ALERT_ACKNOWLEDGED</option>
            <option value="EVIDENCE_VERIFIED">EVIDENCE_VERIFIED</option>
          </select>
        </div>

        <div className="text-slate-400 text-xs">
          TOTAL LOG RECORDS: <strong className="text-blue-400">{logs.length}</strong>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="p-3 rounded-lg bg-red-950/60 border border-red-800/80 text-xs text-red-300 flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-red-400 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Audit Logs Table */}
      <Card className="bg-surface-200 border-surface-border p-0 overflow-hidden">
        <div className="overflow-x-auto custom-scrollbar">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-surface-border bg-surface-300/80 text-slate-400 font-mono text-[11px]">
                <th className="py-3 px-4">TIMESTAMP (UTC)</th>
                <th className="py-3 px-4">ACTION</th>
                <th className="py-3 px-4">RESOURCE TYPE</th>
                <th className="py-3 px-4">ACTOR / USER ID</th>
                <th className="py-3 px-4">FORENSIC METADATA</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-surface-border text-slate-200">
              {logs.length === 0 && !isLoading ? (
                <tr>
                  <td colSpan={5} className="py-8 text-center text-slate-500">
                    No audit records match the selected filter.
                  </td>
                </tr>
              ) : (
                logs.map((log) => (
                  <tr key={log.id} className="hover:bg-surface-100/50 transition font-mono">
                    <td className="py-3 px-4 whitespace-nowrap text-slate-400 text-[11px]">
                      {formatDate(log.timestamp)}
                    </td>
                    <td className="py-3 px-4 whitespace-nowrap">
                      <span className={`px-2 py-0.5 rounded border text-[10px] font-bold ${getActionBadgeClass(log.action)}`}>
                        {log.action}
                      </span>
                    </td>
                    <td className="py-3 px-4 whitespace-nowrap text-slate-300">
                      {log.resource_type} {log.resource_id ? `(${log.resource_id.slice(0, 8)}...)` : ""}
                    </td>
                    <td className="py-3 px-4 whitespace-nowrap text-slate-400">
                      {log.user_id ? log.user_id.slice(0, 8) + "..." : "SYSTEM / AI"}
                    </td>
                    <td className="py-3 px-4 text-[11px] text-slate-400 font-mono break-all">
                      {JSON.stringify(log.metadata || {})}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
