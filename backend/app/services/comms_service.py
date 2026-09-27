from __future__ import annotations

from sqlalchemy.orm import Session

from ..ai import generation
from ..db import models
from . import audit_service, impact_service


def generate_comms_plan(db: Session, project_id: int) -> list[models.CommsPlanItemRow]:
    analysis = impact_service.get_current_analysis(db, project_id)
    if not analysis:
        raise ValueError("Run impact analysis before generating a communication plan.")

    result = generation.generate_comms_plan(impact_service.analysis_to_json(analysis))

    db.query(models.CommsPlanItemRow).filter_by(project_id=project_id).delete()
    rows = []
    for i, item in enumerate(result.items):
        row = models.CommsPlanItemRow(
            project_id=project_id,
            audience=item.audience,
            key_message=item.key_message,
            channel=item.channel,
            owner=item.owner,
            timing=item.timing,
            order_index=i,
        )
        db.add(row)
        rows.append(row)

    audit_service.write_audit(db, project_id, "comms_plan", None, "generated", detail={"count": len(rows)})
    db.commit()
    for row in rows:
        db.refresh(row)
    return rows


def list_comms_plan(db: Session, project_id: int) -> list[models.CommsPlanItemRow]:
    return (
        db.query(models.CommsPlanItemRow)
        .filter_by(project_id=project_id)
        .order_by(models.CommsPlanItemRow.order_index)
        .all()
    )


def update_comms_plan_item(db: Session, row: models.CommsPlanItemRow, updates: dict) -> models.CommsPlanItemRow:
    for field, value in updates.items():
        setattr(row, field, value)
    db.flush()
    audit_service.write_audit(db, row.project_id, "comms_plan_item", row.id, "updated")
    db.commit()
    db.refresh(row)
    return row


def generate_communication_package(db: Session, project_id: int) -> models.CommunicationPackageRow:
    analysis = impact_service.get_current_analysis(db, project_id)
    if not analysis:
        raise ValueError("Run impact analysis before generating communications.")

    result = generation.generate_communications(impact_service.analysis_to_json(analysis))

    db.query(models.CommunicationPackageRow).filter_by(project_id=project_id).delete()
    db.query(models.ChecklistItemRow).filter_by(project_id=project_id).delete()

    package = models.CommunicationPackageRow(
        project_id=project_id,
        employee_subject=result.employee_announcement.subject,
        employee_body=result.employee_announcement.body,
        manager_subject=result.manager_communication.subject,
        manager_body=result.manager_communication.body,
        manager_talking_points=result.manager_communication.talking_points,
        faq=[f.model_dump() for f in result.faq],
        readiness_score=result.readiness_summary.readiness_score,
        readiness_rationale=result.readiness_summary.rationale,
        readiness_top_risks=result.readiness_summary.top_risks,
        readiness_next_steps=result.readiness_summary.recommended_next_steps,
    )
    db.add(package)

    for i, item in enumerate(result.training_checklist):
        db.add(
            models.ChecklistItemRow(
                project_id=project_id, checklist_type="training", item=item.item, owner=item.owner,
                due=item.due, order_index=i,
            )
        )
    for i, item in enumerate(result.implementation_checklist):
        db.add(
            models.ChecklistItemRow(
                project_id=project_id, checklist_type="implementation", item=item.item, owner=item.owner,
                due=item.due, order_index=i,
            )
        )

    audit_service.write_audit(db, project_id, "communication_package", None, "generated")
    db.commit()
    db.refresh(package)
    return package


def get_communication_package(db: Session, project_id: int) -> models.CommunicationPackageRow | None:
    return db.query(models.CommunicationPackageRow).filter_by(project_id=project_id).first()


def list_checklist(db: Session, project_id: int, checklist_type: str | None = None) -> list[models.ChecklistItemRow]:
    q = db.query(models.ChecklistItemRow).filter_by(project_id=project_id)
    if checklist_type:
        q = q.filter_by(checklist_type=checklist_type)
    return q.order_by(models.ChecklistItemRow.checklist_type, models.ChecklistItemRow.order_index).all()


def update_checklist_item(db: Session, row: models.ChecklistItemRow, updates: dict) -> models.ChecklistItemRow:
    for field, value in updates.items():
        setattr(row, field, value)
    db.flush()
    audit_service.write_audit(db, row.project_id, "checklist_item", row.id, "updated")
    db.commit()
    db.refresh(row)
    return row
