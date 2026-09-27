import { client } from './client'
import type { DocumentDiffAnalysis } from './types'

export const diffApi = {
  compare: (projectId: number, question: string) =>
    client.post<DocumentDiffAnalysis>(`/api/v1/projects/${projectId}/diff/compare`, { question }).then((r) => r.data),
  list: (projectId: number) =>
    client.get<DocumentDiffAnalysis[]>(`/api/v1/projects/${projectId}/diff`).then((r) => r.data),
}
