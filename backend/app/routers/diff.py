from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..dependencies import get_db
from ..schemas.diff import DiffRequest, DocumentDiffAnalysisOut
from ..services import diff_service

router = APIRouter(prefix="/api/v1/projects/{project_id}/diff", tags=["diff"])


@router.post("/compare", response_model=DocumentDiffAnalysisOut)
def compare_documents(project_id: int, payload: DiffRequest, db: Session = Depends(get_db)):
    try:
        return diff_service.compare(db, project_id, payload.question)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("", response_model=list[DocumentDiffAnalysisOut])
def list_diffs(project_id: int, db: Session = Depends(get_db)):
    return diff_service.list_diffs(db, project_id)
