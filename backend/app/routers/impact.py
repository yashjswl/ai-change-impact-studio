from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import models
from ..dependencies import get_db
from ..schemas.impact import AnalyzeRequest, ChangeImpactAnalysisOut, StakeholderImpactOut, StakeholderImpactUpdate
from ..services import impact_service

router = APIRouter(prefix="/api/v1/projects/{project_id}", tags=["impact"])


@router.post("/impact-analysis/generate", response_model=ChangeImpactAnalysisOut)
def generate_impact_analysis(project_id: int, payload: AnalyzeRequest, db: Session = Depends(get_db)):
    try:
        return impact_service.generate_and_persist_analysis(
            db, project_id, payload.change_description, payload.ground_in_documents
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/impact-analysis", response_model=ChangeImpactAnalysisOut)
def get_impact_analysis(project_id: int, db: Session = Depends(get_db)):
    analysis = impact_service.get_current_analysis(db, project_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="No impact analysis generated yet")
    return analysis


@router.patch("/stakeholder-impacts/{stakeholder_id}", response_model=StakeholderImpactOut)
def update_stakeholder_impact(
    project_id: int, stakeholder_id: int, payload: StakeholderImpactUpdate, db: Session = Depends(get_db)
):
    row = db.get(models.StakeholderImpactRow, stakeholder_id)
    if not row or row.analysis.project_id != project_id:
        raise HTTPException(status_code=404, detail="Stakeholder impact not found")
    return impact_service.update_stakeholder(db, row, payload.model_dump(exclude_unset=True))
