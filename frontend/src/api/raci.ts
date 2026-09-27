import { client } from './client'
import type { RaciItem } from './types'

export const raciApi = {
  generate: (projectId: number) =>
    client.post<RaciItem[]>(`/api/v1/projects/${projectId}/raci/generate`).then((r) => r.data),
  list: (projectId: number) => client.get<RaciItem[]>(`/api/v1/projects/${projectId}/raci`).then((r) => r.data),
  create: (projectId: number, payload: Partial<RaciItem>) =>
    client.post<RaciItem>(`/api/v1/projects/${projectId}/raci`, payload).then((r) => r.data),
  update: (itemId: number, updates: Partial<RaciItem>) =>
    client.patch<RaciItem>(`/api/v1/raci/${itemId}`, updates).then((r) => r.data),
  remove: (itemId: number) => client.delete(`/api/v1/raci/${itemId}`),
}
