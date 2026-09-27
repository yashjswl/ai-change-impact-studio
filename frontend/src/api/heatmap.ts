import { client } from './client'
import type { HeatmapCell } from './types'

export const heatmapApi = {
  get: (projectId: number) => client.get<HeatmapCell[]>(`/api/v1/projects/${projectId}/heatmap`).then((r) => r.data),
}
