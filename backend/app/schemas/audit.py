from __future__ import annotations

import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AuditLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: Optional[int]
    entity_type: str
    entity_id: Optional[int]
    action: str
    actor: str
    detail: dict
    created_at: datetime.datetime
