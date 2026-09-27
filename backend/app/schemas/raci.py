from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class RaciItemCreate(BaseModel):
    workstream: str
    activity: str
    responsible: str = ""
    accountable: str = ""
    consulted: str = ""
    informed: str = ""


class RaciItemUpdate(BaseModel):
    workstream: str | None = None
    activity: str | None = None
    responsible: str | None = None
    accountable: str | None = None
    consulted: str | None = None
    informed: str | None = None


class RaciItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    workstream: str
    activity: str
    responsible: str
    accountable: str
    consulted: str
    informed: str
    order_index: int
