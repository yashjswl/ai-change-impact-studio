import { client } from './client'
import type { DocumentItem } from './types'

export const documentsApi = {
  list: (projectId: number) =>
    client.get<DocumentItem[]>(`/api/v1/projects/${projectId}/documents`).then((r) => r.data),
  upload: (projectId: number, file: File, docType: string) => {
    const form = new FormData()
    form.append('file', file)
    form.append('doc_type', docType)
    return client
      .post<DocumentItem>(`/api/v1/projects/${projectId}/documents`, form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      .then((r) => r.data)
  },
  loadSamples: (projectId: number) =>
    client.post<DocumentItem[]>(`/api/v1/projects/${projectId}/documents/load-samples`).then((r) => r.data),
  remove: (projectId: number, documentId: number) =>
    client.delete(`/api/v1/projects/${projectId}/documents/${documentId}`),
}
