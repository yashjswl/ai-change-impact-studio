from __future__ import annotations

from pydantic import BaseModel


class HeatmapCell(BaseModel):
    stakeholder_id: int
    stakeholder: str
    impact_score: float
    readiness_score: float
    heat_rating: str
    barrier_dimension: str | None
