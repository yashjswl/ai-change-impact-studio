from __future__ import annotations

from sqlalchemy.orm import Session

from ..db import models


def write_audit(
    db: Session,
    project_id: int | None,
    entity_type: str,
    entity_id: int | None,
    action: str,
    actor: str = "system",
    detail: dict | None = None,
) -> models.AuditLog:
    entry = models.AuditLog(
        project_id=project_id,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        actor=actor,
        detail=detail or {},
    )
    db.add(entry)
    db.flush()
    return entry
