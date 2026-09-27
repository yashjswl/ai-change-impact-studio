import { client } from './client'
import type { RaidItem } from './types'

export const raidApi = {
  generate: (projectId: number) =>
    client.post<RaidItem[]>(`/api/v1/projects/${projectId}/raid/generate`).then((r) => r.data),
  list: (projectId: number) => client.get<RaidItem[]>(`/api/v1/projects/${projectId}/raid`).then((r) => r.data),
  create: (projectId: number, payload: Partial<RaidItem>) =>
    client.post<RaidItem>(`/api/v1/projects/${projectId}/raid`, payload).then((r) => r.data),
  update: (itemId: number, updates: Partial<RaidItem>) =>
    client.patch<RaidItem>(`/api/v1/raid/${itemId}`, updates).then((r) => r.data),
  remove: (itemId: number) => client.delete(`/api/v1/raid/${itemId}`),
}
