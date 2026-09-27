from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db import models
from ..dependencies import get_db
from ..schemas.audit import AuditLogOut

router = APIRouter(prefix="/api/v1/projects/{project_id}/audit-log", tags=["audit"])


@router.get("", response_model=list[AuditLogOut])
def get_audit_log(project_id: int, db: Session = Depends(get_db)):
    return (
        db.query(models.AuditLog)
        .filter_by(project_id=project_id)
        .order_by(models.AuditLog.created_at.desc())
        .limit(500)
        .all()
    )
