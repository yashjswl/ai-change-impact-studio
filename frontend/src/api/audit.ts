import { client } from './client'
import type { AuditLogEntry } from './types'

export const auditApi = {
  list: (projectId: number) =>
    client.get<AuditLogEntry[]>(`/api/v1/projects/${projectId}/audit-log`).then((r) => r.data),
}
