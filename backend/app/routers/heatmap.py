from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..dependencies import get_db
from ..schemas.heatmap import HeatmapCell
from ..services import impact_service

router = APIRouter(prefix="/api/v1/projects/{project_id}/heatmap", tags=["heatmap"])


@router.get("", response_model=list[HeatmapCell])
def get_heatmap(project_id: int, db: Session = Depends(get_db)):
    analysis = impact_service.get_current_analysis(db, project_id)
    if not analysis:
        return []
    return [
        HeatmapCell(
            stakeholder_id=s.id,
            stakeholder=s.stakeholder,
            impact_score=s.impact_score,
            readiness_score=s.readiness_score,
            heat_rating=s.heat_rating,
            barrier_dimension=s.adkar_barrier_dimension,
        )
        for s in analysis.stakeholder_impacts
    ]
