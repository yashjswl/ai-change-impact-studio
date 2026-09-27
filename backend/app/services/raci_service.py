from __future__ import annotations

from sqlalchemy.orm import Session

from ..ai import generation
from ..db import models
from . import audit_service, impact_service


def generate(db: Session, project_id: int) -> list[models.RaciItemRow]:
    analysis = impact_service.get_current_analysis(db, project_id)
    if not analysis:
        raise ValueError("Run impact analysis before generating a RACI matrix.")

    result = generation.generate_raci(impact_service.analysis_to_json(analysis))

    db.query(models.RaciItemRow).filter_by(project_id=project_id).delete()
    rows = []
    for i, item in enumerate(result.items):
        row = models.RaciItemRow(
            project_id=project_id,
            workstream=item.workstream,
            activity=item.activity,
            responsible=item.responsible,
            accountable=item.accountable,
            consulted=item.consulted,
            informed=item.informed,
            order_index=i,
        )
        db.add(row)
        rows.append(row)

    audit_service.write_audit(db, project_id, "raci", None, "generated", detail={"count": len(rows)})
    db.commit()
    for row in rows:
        db.refresh(row)
    return rows


def list_items(db: Session, project_id: int) -> list[models.RaciItemRow]:
    return db.query(models.RaciItemRow).filter_by(project_id=project_id).order_by(models.RaciItemRow.order_index).all()


def create_item(db: Session, project_id: int, payload: dict) -> models.RaciItemRow:
    max_order = db.query(models.RaciItemRow).filter_by(project_id=project_id).count()
    row = models.RaciItemRow(project_id=project_id, order_index=max_order, **payload)
    db.add(row)
    db.flush()
    audit_service.write_audit(db, project_id, "raci_item", row.id, "created")
    db.commit()
    db.refresh(row)
    return row


def update_item(db: Session, row: models.RaciItemRow, updates: dict) -> models.RaciItemRow:
    for field, value in updates.items():
        setattr(row, field, value)
    db.flush()
    audit_service.write_audit(db, row.project_id, "raci_item", row.id, "updated")
    db.commit()
    db.refresh(row)
    return row


def delete_item(db: Session, row: models.RaciItemRow) -> None:
    audit_service.write_audit(db, row.project_id, "raci_item", row.id, "deleted")
    db.delete(row)
    db.commit()
