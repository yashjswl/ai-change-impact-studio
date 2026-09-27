from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..dependencies import get_db
from ..schemas.approval import ApprovalCreate, ApprovalOut
from ..services import approval_service

router = APIRouter(prefix="/api/v1/projects/{project_id}/approvals", tags=["approvals"])


@router.post("", response_model=ApprovalOut)
def create_approval(project_id: int, payload: ApprovalCreate, db: Session = Depends(get_db)):
    return approval_service.create_approval(db, project_id, payload.model_dump())


@router.get("", response_model=list[ApprovalOut])
def list_approvals(
    project_id: int,
    artifact_type: str | None = None,
    artifact_id: int | None = None,
    db: Session = Depends(get_db),
):
    return approval_service.list_approvals(db, project_id, artifact_type, artifact_id)


@router.get("/current", response_model=list[ApprovalOut])
def current_approvals(project_id: int, db: Session = Depends(get_db)):
    return list(approval_service.current_statuses(db, project_id).values())
