import { fetchApi } from "./apiClient";
import { AuditLogRecord } from "../types/audit";

export interface AuditLogQueryParams {
  user_id?: string;
  action?: string;
  resource_type?: string;
  limit?: number;
  offset?: number;
}

export const auditService = {
  async getAuditLogs(params: AuditLogQueryParams = {}): Promise<AuditLogRecord[]> {
    const query = new URLSearchParams();
    if (params.user_id) query.append("user_id", params.user_id);
    if (params.action) query.append("action", params.action);
    if (params.resource_type) query.append("resource_type", params.resource_type);
    if (params.limit) query.append("limit", params.limit.toString());
    if (params.offset) query.append("offset", params.offset.toString());

    const qs = query.toString() ? `?${query.toString()}` : "";
    const rawLogs = await fetchApi<any[]>(`/audit-logs${qs}`);

    return rawLogs.map((log) => ({
      id: log.id,
      user_id: log.user_id,
      action: log.action,
      resource_type: log.resource_type,
      resource_id: log.resource_id,
      timestamp: log.timestamp,
      metadata: log.metadata || log.log_metadata || {},
    }));
  },
};
