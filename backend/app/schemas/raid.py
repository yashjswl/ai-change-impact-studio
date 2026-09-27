from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict


class RaidItemCreate(BaseModel):
    category: str = "Risk"
    description: str
    severity: str = "Medium"
    likelihood: str = "Medium"
    owner: str = ""
    status: str = "Open"
    mitigation: str = ""
    due_date: Optional[str] = None


class RaidItemUpdate(BaseModel):
    category: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    likelihood: Optional[str] = None
    owner: Optional[str] = None
    status: Optional[str] = None
    mitigation: Optional[str] = None
    due_date: Optional[str] = None


class RaidItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    category: str
    description: str
    severity: str
    likelihood: str
    owner: str
    status: str
    mitigation: str
    due_date: Optional[str]
