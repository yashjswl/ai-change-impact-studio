from __future__ import annotations

import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class AnalyzeRequest(BaseModel):
    change_description: str
    ground_in_documents: bool = True


class StakeholderImpactOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    analysis_id: int
    stakeholder: str
    what_changes: str
    what_is_impacted: list[str]
    what_to_learn: list[str]
    resistance_risk: list[str]
    action_required: list[str]
    impact_type: list[str]
    impact_severity: int
    adkar_awareness: int
    adkar_desire: int
    adkar_knowledge: int
    adkar_ability: int
    adkar_reinforcement: int
    adkar_barrier_dimension: Optional[str]
    adkar_rationale: str
    readiness_score: float
    impact_score: float
    heat_rating: str
    edited_by_human: bool
    updated_at: datetime.datetime


class StakeholderImpactUpdate(BaseModel):
    what_changes: Optional[str] = None
    what_is_impacted: Optional[list[str]] = None
    what_to_learn: Optional[list[str]] = None
    resistance_risk: Optional[list[str]] = None
    action_required: Optional[list[str]] = None
    impact_type: Optional[list[str]] = None
    impact_severity: Optional[int] = Field(default=None, ge=1, le=5)
    adkar_awareness: Optional[int] = Field(default=None, ge=1, le=5)
    adkar_desire: Optional[int] = Field(default=None, ge=1, le=5)
    adkar_knowledge: Optional[int] = Field(default=None, ge=1, le=5)
    adkar_ability: Optional[int] = Field(default=None, ge=1, le=5)
    adkar_reinforcement: Optional[int] = Field(default=None, ge=1, le=5)
    adkar_rationale: Optional[str] = None


class ChangeImpactAnalysisOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    change_title: str
    change_summary: str
    overall_risks: list[str]
    success_factors: list[str]
    is_current: bool
    created_at: datetime.datetime
    stakeholder_impacts: list[StakeholderImpactOut]
