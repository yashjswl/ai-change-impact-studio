from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict


class CommsPlanItemCreate(BaseModel):
    audience: str
    key_message: str
    channel: str = ""
    owner: str = ""
    timing: str = ""


class CommsPlanItemUpdate(BaseModel):
    audience: Optional[str] = None
    key_message: Optional[str] = None
    channel: Optional[str] = None
    owner: Optional[str] = None
    timing: Optional[str] = None


class CommsPlanItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    audience: str
    key_message: str
    channel: str
    owner: str
    timing: str
    order_index: int


class FaqItemOut(BaseModel):
    question: str
    answer: str


class CommunicationPackageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    employee_subject: str
    employee_body: str
    manager_subject: str
    manager_body: str
    manager_talking_points: list[str]
    faq: list[dict]
    readiness_score: int
    readiness_rationale: str
    readiness_top_risks: list[str]
    readiness_next_steps: list[str]


class ChecklistItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    checklist_type: str
    item: str
    owner: str
    due: Optional[str]
    is_done: bool
    order_index: int


class ChecklistItemUpdate(BaseModel):
    item: Optional[str] = None
    owner: Optional[str] = None
    due: Optional[str] = None
    is_done: Optional[bool] = None
