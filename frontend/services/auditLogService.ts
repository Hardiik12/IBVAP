import { fetchApi } from "./apiClient";

export interface AuditLogItem {
  id: string;
  user_id?: string;
  action: string;
  resource_type: string;
  resource_id?: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

export const auditLogService = {
  async getAuditLogs(params: Record<string, string> = {}): Promise<AuditLogItem[]> {
    const query = new URLSearchParams(params).toString();
    const qs = query ? `?${query}` : "";
    return await fetchApi<AuditLogItem[]>(`/audit-logs${qs}`);
  },

  async clearAuditLogs(): Promise<{ message: string; cleared_count: number }> {
    return await fetchApi<{ message: string; cleared_count: number }>("/audit-logs", {
      method: "DELETE",
    });
  },
};
