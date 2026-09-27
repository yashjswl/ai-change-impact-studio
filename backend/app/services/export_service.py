from __future__ import annotations

import datetime

from sqlalchemy.orm import Session

from ..config import EXPORT_DIR
from ..db import models
from ..exporters import docx_export, pptx_export
from . import audit_service, comms_service, impact_service, raci_service, raid_service


def _export_path(project_id: int, export_type: str, ext: str) -> str:
    project_dir = EXPORT_DIR / str(project_id)
    project_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = project_dir / f"{export_type}_{timestamp}.{ext}"
    return str(path)


def _record_export(db: Session, project_id: int, export_type: str, file_path: str) -> models.Export:
    export = models.Export(project_id=project_id, export_type=export_type, file_path=file_path)
    db.add(export)
    db.flush()
    audit_service.write_audit(db, project_id, "export", export.id, "exported", detail={"export_type": export_type})
    db.commit()
    db.refresh(export)
    return export


def export_impact_onepager(db: Session, project: models.Project) -> models.Export:
    analysis = impact_service.get_current_analysis(db, project.id)
    if not analysis:
        raise ValueError("Run impact analysis before exporting the impact assessment.")

    doc = docx_export.build_impact_onepager(project, analysis)
    path = _export_path(project.id, "docx_impact_onepager", "docx")
    doc.save(path)
    return _record_export(db, project.id, "docx_impact_onepager", path)


def export_comms_package(db: Session, project: models.Project) -> models.Export:
    package = comms_service.get_communication_package(db, project.id)
    if not package:
        raise ValueError("Generate the communication package before exporting it.")

    training = comms_service.list_checklist(db, project.id, "training")
    implementation = comms_service.list_checklist(db, project.id, "implementation")
    doc = docx_export.build_comms_package(project, package, training, implementation)
    path = _export_path(project.id, "docx_comms_package", "docx")
    doc.save(path)
    return _record_export(db, project.id, "docx_comms_package", path)


def export_executive_summary(db: Session, project: models.Project) -> models.Export:
    analysis = impact_service.get_current_analysis(db, project.id)
    stakeholders = analysis.stakeholder_impacts if analysis else []

    raid_items = raid_service.list_items(db, project.id)
    top_risks = [
        r.description
        for r in raid_items
        if r.category == "Risk" and r.severity in ("High", "Critical")
    ][:6]

    raci_items = raci_service.list_items(db, project.id)

    package = comms_service.get_communication_package(db, project.id)
    next_steps = package.readiness_next_steps if package else []

    prs = pptx_export.build_executive_summary(project, stakeholders, top_risks, raci_items, next_steps)
    path = _export_path(project.id, "pptx_exec_summary", "pptx")
    prs.save(path)
    return _record_export(db, project.id, "pptx_exec_summary", path)


def get_export(db: Session, export_id: int) -> models.Export | None:
    return db.get(models.Export, export_id)
