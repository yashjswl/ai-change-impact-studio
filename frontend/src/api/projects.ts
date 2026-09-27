import { client } from './client'
import type { Project, ProjectDashboard } from './types'

export const projectsApi = {
  list: () => client.get<Project[]>('/api/v1/projects').then((r) => r.data),
  get: (id: number) => client.get<Project>(`/api/v1/projects/${id}`).then((r) => r.data),
  create: (payload: { name: string; description?: string; change_type?: string }) =>
    client.post<Project>('/api/v1/projects', payload).then((r) => r.data),
  update: (id: number, payload: Partial<Project>) =>
    client.patch<Project>(`/api/v1/projects/${id}`, payload).then((r) => r.data),
  remove: (id: number) => client.delete(`/api/v1/projects/${id}`),
  dashboard: (id: number) => client.get<ProjectDashboard>(`/api/v1/projects/${id}/dashboard`).then((r) => r.data),
  portfolio: () => client.get<ProjectDashboard[]>('/api/v1/portfolio').then((r) => r.data),
}
