from __future__ import annotations

import datetime

from pydantic import BaseModel, ConfigDict


class ExportOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    export_type: str
    file_path: str
    generated_by: str
    created_at: datetime.datetime
