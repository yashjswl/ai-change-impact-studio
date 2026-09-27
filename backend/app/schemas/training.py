from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict


class TrainingItemCreate(BaseModel):
    role: str
    current_capability: str = ""
    required_capability: str = ""
    gap: str = ""
    training_action: str = ""
    owner: str = ""
    due_date: Optional[str] = None
    priority: str = "Medium"


class TrainingItemUpdate(BaseModel):
    role: Optional[str] = None
    current_capability: Optional[str] = None
    required_capability: Optional[str] = None
    gap: Optional[str] = None
    training_action: Optional[str] = None
    owner: Optional[str] = None
    due_date: Optional[str] = None
    priority: Optional[str] = None


class TrainingItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    role: str
    current_capability: str
    required_capability: str
    gap: str
    training_action: str
    owner: str
    due_date: Optional[str]
    priority: str
