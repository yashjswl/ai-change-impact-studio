import { client } from './client'
import type { TrainingItem } from './types'

export const trainingApi = {
  generate: (projectId: number) =>
    client.post<TrainingItem[]>(`/api/v1/projects/${projectId}/training-matrix/generate`).then((r) => r.data),
  list: (projectId: number) =>
    client.get<TrainingItem[]>(`/api/v1/projects/${projectId}/training-matrix`).then((r) => r.data),
  create: (projectId: number, payload: Partial<TrainingItem>) =>
    client.post<TrainingItem>(`/api/v1/projects/${projectId}/training-matrix`, payload).then((r) => r.data),
  update: (itemId: number, updates: Partial<TrainingItem>) =>
    client.patch<TrainingItem>(`/api/v1/training-matrix/${itemId}`, updates).then((r) => r.data),
  remove: (itemId: number) => client.delete(`/api/v1/training-matrix/${itemId}`),
}
