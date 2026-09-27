from __future__ import annotations

import datetime

from pydantic import BaseModel, ConfigDict


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    filename: str
    doc_type: str
    char_count: int
    uploaded_at: datetime.datetime
