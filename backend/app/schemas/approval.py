from __future__ import annotations

import datetime

from pydantic import BaseModel, ConfigDict


class ApprovalCreate(BaseModel):
    artifact_type: str
    artifact_id: int
    reviewer_name: str
    status: str  # approved | rejected | pending
    comments: str = ""


class ApprovalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    artifact_type: str
    artifact_id: int
    reviewer_name: str
    status: str
    comments: str
    created_at: datetime.datetime
