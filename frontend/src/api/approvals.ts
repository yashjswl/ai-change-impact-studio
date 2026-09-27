import { client } from './client'
import type { Approval } from './types'

export const approvalsApi = {
  create: (
    projectId: number,
    payload: { artifact_type: string; artifact_id: number; reviewer_name: string; status: string; comments?: string },
  ) => client.post<Approval>(`/api/v1/projects/${projectId}/approvals`, payload).then((r) => r.data),
  list: (projectId: number, artifactType?: string, artifactId?: number) =>
    client
      .get<Approval[]>(`/api/v1/projects/${projectId}/approvals`, {
        params: { artifact_type: artifactType, artifact_id: artifactId },
      })
      .then((r) => r.data),
  current: (projectId: number) =>
    client.get<Approval[]>(`/api/v1/projects/${projectId}/approvals/current`).then((r) => r.data),
}
