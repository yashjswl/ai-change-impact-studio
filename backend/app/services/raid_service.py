from __future__ import annotations

from sqlalchemy.orm import Session

from ..ai import generation
from ..db import models
from . import audit_service, impact_service


def generate(db: Session, project_id: int) -> list[models.RaidItemRow]:
    analysis = impact_service.get_current_analysis(db, project_id)
    if not analysis:
        raise ValueError("Run impact analysis before generating a RAID log.")

    result = generation.generate_raid(impact_service.analysis_to_json(analysis))

    db.query(models.RaidItemRow).filter_by(project_id=project_id).delete()
    rows = []
    for item in result.items:
        row = models.RaidItemRow(
            project_id=project_id,
            category=item.category,
            description=item.description,
            severity=item.severity,
            likelihood=item.likelihood,
            owner=item.owner,
            status=item.status,
            mitigation=item.mitigation,
            due_date=item.due_date,
        )
        db.add(row)
        rows.append(row)

    audit_service.write_audit(db, project_id, "raid", None, "generated", detail={"count": len(rows)})
    db.commit()
    for row in rows:
        db.refresh(row)
    return rows


def list_items(db: Session, project_id: int) -> list[models.RaidItemRow]:
    return db.query(models.RaidItemRow).filter_by(project_id=project_id).order_by(models.RaidItemRow.id).all()


def create_item(db: Session, project_id: int, payload: dict) -> models.RaidItemRow:
    row = models.RaidItemRow(project_id=project_id, **payload)
    db.add(row)
    db.flush()
    audit_service.write_audit(db, project_id, "raid_item", row.id, "created")
    db.commit()
    db.refresh(row)
    return row


def update_item(db: Session, row: models.RaidItemRow, updates: dict) -> models.RaidItemRow:
    for field, value in updates.items():
        setattr(row, field, value)
    db.flush()
    audit_service.write_audit(db, row.project_id, "raid_item", row.id, "updated")
    db.commit()
    db.refresh(row)
    return row


def delete_item(db: Session, row: models.RaidItemRow) -> None:
    audit_service.write_audit(db, row.project_id, "raid_item", row.id, "deleted")
    db.delete(row)
    db.commit()
