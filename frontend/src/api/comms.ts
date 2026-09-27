import { client } from './client'
import type { ChecklistItem, CommsPlanItem, CommunicationPackage } from './types'

export const commsApi = {
  generatePlan: (projectId: number) =>
    client.post<CommsPlanItem[]>(`/api/v1/projects/${projectId}/comms-plan/generate`).then((r) => r.data),
  listPlan: (projectId: number) =>
    client.get<CommsPlanItem[]>(`/api/v1/projects/${projectId}/comms-plan`).then((r) => r.data),
  updatePlanItem: (itemId: number, updates: Partial<CommsPlanItem>) =>
    client.patch<CommsPlanItem>(`/api/v1/comms-plan/${itemId}`, updates).then((r) => r.data),

  generatePackage: (projectId: number) =>
    client
      .post<CommunicationPackage>(`/api/v1/projects/${projectId}/communication-package/generate`)
      .then((r) => r.data),
  getPackage: (projectId: number) =>
    client.get<CommunicationPackage>(`/api/v1/projects/${projectId}/communication-package`).then((r) => r.data),

  listChecklist: (projectId: number, checklistType?: 'training' | 'implementation') =>
    client
      .get<ChecklistItem[]>(`/api/v1/projects/${projectId}/checklists`, {
        params: checklistType ? { checklist_type: checklistType } : {},
      })
      .then((r) => r.data),
  updateChecklistItem: (itemId: number, updates: Partial<ChecklistItem>) =>
    client.patch<ChecklistItem>(`/api/v1/checklist-items/${itemId}`, updates).then((r) => r.data),
}
