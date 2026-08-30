export interface AuditLogRecord {
  id: string;
  user_id?: string;
  action: string;
  resource_type: string;
  resource_id?: string;
  timestamp: string;
  metadata?: Record<string, any>;
}
