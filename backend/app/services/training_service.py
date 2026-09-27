from __future__ import annotations

from sqlalchemy.orm import Session

from ..ai import generation
from ..db import models
from . import audit_service, impact_service


def generate(db: Session, project_id: int) -> list[models.TrainingMatrixItemRow]:
    analysis = impact_service.get_current_analysis(db, project_id)
    if not analysis:
        raise ValueError("Run impact analysis before generating a training needs matrix.")

    result = generation.generate_training_matrix(impact_service.analysis_to_json(analysis))

    db.query(models.TrainingMatrixItemRow).filter_by(project_id=project_id).delete()
    rows = []
    for item in result.items:
        row = models.TrainingMatrixItemRow(
            project_id=project_id,
            role=item.role,
            current_capability=item.current_capability,
            required_capability=item.required_capability,
            gap=item.gap,
            training_action=item.training_action,
            owner=item.owner,
            due_date=item.due_date,
            priority=item.priority,
        )
        db.add(row)
        rows.append(row)

    audit_service.write_audit(db, project_id, "training_matrix", None, "generated", detail={"count": len(rows)})
    db.commit()
    for row in rows:
        db.refresh(row)
    return rows


def list_items(db: Session, project_id: int) -> list[models.TrainingMatrixItemRow]:
    return db.query(models.TrainingMatrixItemRow).filter_by(project_id=project_id).order_by(
        models.TrainingMatrixItemRow.id
    ).all()


def create_item(db: Session, project_id: int, payload: dict) -> models.TrainingMatrixItemRow:
    row = models.TrainingMatrixItemRow(project_id=project_id, **payload)
    db.add(row)
    db.flush()
    audit_service.write_audit(db, project_id, "training_item", row.id, "created")
    db.commit()
    db.refresh(row)
    return row


def update_item(db: Session, row: models.TrainingMatrixItemRow, updates: dict) -> models.TrainingMatrixItemRow:
    for field, value in updates.items():
        setattr(row, field, value)
    db.flush()
    audit_service.write_audit(db, row.project_id, "training_item", row.id, "updated")
    db.commit()
    db.refresh(row)
    return row


def delete_item(db: Session, row: models.TrainingMatrixItemRow) -> None:
    audit_service.write_audit(db, row.project_id, "training_item", row.id, "deleted")
    db.delete(row)
    db.commit()
