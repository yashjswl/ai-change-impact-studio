export interface Project {
  id: number
  name: string
  description: string
  change_type: string
  status: string
  created_at: string
  updated_at: string
}

export interface ProjectDashboard {
  project: Project
  readiness_score: number | null
  red_count: number
  amber_count: number
  green_count: number
  stakeholder_count: number
  top_risks: string[]
  open_raid_count: number
  document_count: number
}

export interface DocumentItem {
  id: number
  project_id: number
  filename: string
  doc_type: string
  char_count: number
  uploaded_at: string
}

export interface StakeholderImpact {
  id: number
  analysis_id: number
  stakeholder: string
  what_changes: string
  what_is_impacted: string[]
  what_to_learn: string[]
  resistance_risk: string[]
  action_required: string[]
  impact_type: string[]
  impact_severity: number
  adkar_awareness: number
  adkar_desire: number
  adkar_knowledge: number
  adkar_ability: number
  adkar_reinforcement: number
  adkar_barrier_dimension: string | null
  adkar_rationale: string
  readiness_score: number
  impact_score: number
  heat_rating: 'Red' | 'Amber' | 'Green'
  edited_by_human: boolean
  updated_at: string
}

export interface ChangeImpactAnalysis {
  id: number
  project_id: number
  change_title: string
  change_summary: string
  overall_risks: string[]
  success_factors: string[]
  is_current: boolean
  created_at: string
  stakeholder_impacts: StakeholderImpact[]
}

export interface HeatmapCell {
  stakeholder_id: number
  stakeholder: string
  impact_score: number
  readiness_score: number
  heat_rating: 'Red' | 'Amber' | 'Green'
  barrier_dimension: string | null
}

export interface RaciItem {
  id: number
  project_id: number
  workstream: string
  activity: string
  responsible: string
  accountable: string
  consulted: string
  informed: string
  order_index: number
}

export interface RaidItem {
  id: number
  project_id: number
  category: 'Risk' | 'Assumption' | 'Issue' | 'Dependency'
  description: string
  severity: 'Low' | 'Medium' | 'High' | 'Critical'
  likelihood: 'Low' | 'Medium' | 'High'
  owner: string
  status: 'Open' | 'Mitigating' | 'Monitoring' | 'Closed'
  mitigation: string
  due_date: string | null
}

export interface CommsPlanItem {
  id: number
  project_id: number
  audience: string
  key_message: string
  channel: string
  owner: string
  timing: string
  order_index: number
}

export interface FaqItem {
  question: string
  answer: string
}

export interface CommunicationPackage {
  id: number
  project_id: number
  employee_subject: string
  employee_body: string
  manager_subject: string
  manager_body: string
  manager_talking_points: string[]
  faq: FaqItem[]
  readiness_score: number
  readiness_rationale: string
  readiness_top_risks: string[]
  readiness_next_steps: string[]
}

export interface ChecklistItem {
  id: number
  project_id: number
  checklist_type: 'training' | 'implementation'
  item: string
  owner: string
  due: string | null
  is_done: boolean
  order_index: number
}

export interface TrainingItem {
  id: number
  project_id: number
  role: string
  current_capability: string
  required_capability: string
  gap: string
  training_action: string
  owner: string
  due_date: string | null
  priority: 'Low' | 'Medium' | 'High'
}

export interface Citation {
  id: number
  source: string
  excerpt: string
  verified: boolean
  verification_note: string | null
}

export interface DiffFinding {
  id: number
  topic: string
  old_state: string
  new_state: string
  citations: Citation[]
}

export interface DocumentDiffAnalysis {
  id: number
  project_id: number
  question: string
  summary: string
  created_at: string
  findings: DiffFinding[]
}

export interface Approval {
  id: number
  project_id: number
  artifact_type: string
  artifact_id: number
  reviewer_name: string
  status: 'pending' | 'approved' | 'rejected'
  comments: string
  created_at: string
}

export interface AuditLogEntry {
  id: number
  project_id: number | null
  entity_type: string
  entity_id: number | null
  action: string
  actor: string
  detail: Record<string, unknown>
  created_at: string
}

export interface ExportRecord {
  id: number
  project_id: number
  export_type: string
  file_path: string
  generated_by: string
  created_at: string
}
