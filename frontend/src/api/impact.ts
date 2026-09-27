import { client } from './client'
import type { ChangeImpactAnalysis, StakeholderImpact } from './types'

export const impactApi = {
  generate: (projectId: number, changeDescription: string, groundInDocuments: boolean) =>
    client
      .post<ChangeImpactAnalysis>(`/api/v1/projects/${projectId}/impact-analysis/generate`, {
        change_description: changeDescription,
        ground_in_documents: groundInDocuments,
      })
      .then((r) => r.data),
  get: (projectId: number) =>
    client.get<ChangeImpactAnalysis>(`/api/v1/projects/${projectId}/impact-analysis`).then((r) => r.data),
  updateStakeholder: (projectId: number, stakeholderId: number, updates: Partial<StakeholderImpact>) =>
    client
      .patch<StakeholderImpact>(`/api/v1/projects/${projectId}/stakeholder-impacts/${stakeholderId}`, updates)
      .then((r) => r.data),
}
