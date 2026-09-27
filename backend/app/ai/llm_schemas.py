"""Pydantic schemas used as `response_schema` for structured LLM output.
These mirror (and extend) the domain, but are kept separate from the
SQLAlchemy models (`db/models.py`) and the API DTOs (`schemas/`), this is
purely what the model is asked to produce."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class AdkarScore(BaseModel):
    awareness: int = Field(ge=1, le=5, description="Awareness of why the change is needed")
    desire: int = Field(ge=1, le=5, description="Personal motivation to support the change")
    knowledge: int = Field(ge=1, le=5, description="Knowledge of how to change")
    ability: int = Field(ge=1, le=5, description="Demonstrated ability to implement new skills/behaviors")
    reinforcement: int = Field(ge=1, le=5, description="Reinforcement to sustain the change")
    rationale: str = Field(description="1-2 sentence justification for these scores")


class StakeholderImpact(BaseModel):
    stakeholder: str = Field(description="Stakeholder group name, e.g. HR, IT, Managers, Employees, Finance")
    what_changes: str
    what_is_impacted: List[str]
    what_to_learn: List[str]
    resistance_risk: List[str]
    action_required: List[str]
    impact_type: List[str] = Field(description="One or more of: Process, Systems, Role, Policy")
    impact_severity: int = Field(ge=1, le=5, description="1=minimal disruption, 5=critical/transformational")
    adkar: AdkarScore


class ChangeImpactAnalysis(BaseModel):
    change_title: str
    change_summary: str
    stakeholder_impacts: List[StakeholderImpact]
    overall_risks: List[str]
    success_factors: List[str]


class FAQItem(BaseModel):
    question: str
    answer: str


class ChecklistItem(BaseModel):
    item: str
    owner: str
    due: Optional[str] = None


class EmployeeAnnouncement(BaseModel):
    subject: str
    body: str


class ManagerCommunication(BaseModel):
    subject: str
    body: str
    talking_points: List[str]


class ChangeReadinessSummary(BaseModel):
    readiness_score: int = Field(ge=0, le=100)
    rationale: str
    top_risks: List[str]
    recommended_next_steps: List[str]


class CommunicationPackage(BaseModel):
    employee_announcement: EmployeeAnnouncement
    manager_communication: ManagerCommunication
    faq: List[FAQItem]
    training_checklist: List[ChecklistItem]
    implementation_checklist: List[ChecklistItem]
    readiness_summary: ChangeReadinessSummary


class RaciItem(BaseModel):
    workstream: str
    activity: str
    responsible: str
    accountable: str
    consulted: str
    informed: str


class RaciMatrix(BaseModel):
    items: List[RaciItem]


class RaidItem(BaseModel):
    category: str = Field(description="One of: Risk, Assumption, Issue, Dependency")
    description: str
    severity: str = Field(description="One of: Low, Medium, High, Critical")
    likelihood: str = Field(description="One of: Low, Medium, High")
    owner: str
    mitigation: str
    status: str = Field(default="Open", description="One of: Open, Mitigating, Monitoring, Closed")
    due_date: Optional[str] = None


class RaidLog(BaseModel):
    items: List[RaidItem]


class CommsPlanItem(BaseModel):
    audience: str
    key_message: str
    channel: str
    owner: str
    timing: str


class CommunicationPlan(BaseModel):
    items: List[CommsPlanItem]


class TrainingMatrixItem(BaseModel):
    role: str
    current_capability: str
    required_capability: str
    gap: str
    training_action: str
    owner: str
    due_date: Optional[str] = None
    priority: str = Field(description="One of: Low, Medium, High")


class TrainingNeedsMatrix(BaseModel):
    items: List[TrainingMatrixItem]


class Citation(BaseModel):
    source: str = Field(description="Document name the excerpt was retrieved from")
    excerpt: str = Field(description="Short verbatim excerpt supporting the finding")


class DiffFinding(BaseModel):
    topic: str
    old_state: str
    new_state: str
    citations: List[Citation]


class DocumentDiffAnalysis(BaseModel):
    summary: str
    findings: List[DiffFinding]
