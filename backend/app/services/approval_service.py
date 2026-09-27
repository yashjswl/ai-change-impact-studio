from __future__ import annotations

from sqlalchemy.orm import Session

from ..db import models
from . import audit_service


def create_approval(db: Session, project_id: int, payload: dict) -> models.Approval:
    approval = models.Approval(project_id=project_id, **payload)
    db.add(approval)
    db.flush()
    audit_service.write_audit(
        db,
        project_id,
        payload["artifact_type"],
        payload["artifact_id"],
        payload["status"],
        actor=payload.get("reviewer_name", "system"),
        detail={"comments": payload.get("comments", "")},
    )
    db.commit()
    db.refresh(approval)
    return approval


def list_approvals(
    db: Session, project_id: int, artifact_type: str | None = None, artifact_id: int | None = None
) -> list[models.Approval]:
    q = db.query(models.Approval).filter_by(project_id=project_id)
    if artifact_type:
        q = q.filter_by(artifact_type=artifact_type)
    if artifact_id is not None:
        q = q.filter_by(artifact_id=artifact_id)
    return q.order_by(models.Approval.created_at.desc()).all()


def current_statuses(db: Session, project_id: int) -> dict[tuple[str, int], models.Approval]:
    """Latest approval row per (artifact_type, artifact_id), the append-only
    log's derived 'current status' view."""
    all_approvals = (
        db.query(models.Approval).filter_by(project_id=project_id).order_by(models.Approval.created_at).all()
    )
    latest: dict[tuple[str, int], models.Approval] = {}
    for a in all_approvals:
        latest[(a.artifact_type, a.artifact_id)] = a
    return latest
