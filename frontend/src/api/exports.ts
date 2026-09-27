import { API_URL, client } from './client'
import type { ExportRecord } from './types'

export const exportsApi = {
  impactOnepager: (projectId: number) =>
    client.post<ExportRecord>(`/api/v1/projects/${projectId}/exports/docx/impact-onepager`).then((r) => r.data),
  commsPackage: (projectId: number) =>
    client.post<ExportRecord>(`/api/v1/projects/${projectId}/exports/docx/comms-package`).then((r) => r.data),
  executiveSummary: (projectId: number) =>
    client.post<ExportRecord>(`/api/v1/projects/${projectId}/exports/pptx/executive-summary`).then((r) => r.data),
  downloadUrl: (exportId: number) => `${API_URL}/api/v1/exports/${exportId}/download`,
}
