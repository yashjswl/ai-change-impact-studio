from __future__ import annotations

import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ProjectCreate(BaseModel):
    name: str
    description: str = ""
    change_type: str = "Process"


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    change_type: Optional[str] = None
    status: Optional[str] = None


class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    change_type: str
    status: str
    created_at: datetime.datetime
    updated_at: datetime.datetime


class ProjectDashboardOut(BaseModel):
    project: ProjectOut
    readiness_score: Optional[int] = None
    red_count: int = 0
    amber_count: int = 0
    green_count: int = 0
    stakeholder_count: int = 0
    top_risks: list[str] = []
    open_raid_count: int = 0
    document_count: int = 0
