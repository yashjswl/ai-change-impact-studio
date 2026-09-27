from __future__ import annotations

from sqlalchemy.orm import Session

from ..db import models
from ..schemas.project import ProjectCreate, ProjectDashboardOut, ProjectOut, ProjectUpdate
from . import audit_service


def create_project(db: Session, payload: ProjectCreate) -> models.Project:
    project = models.Project(name=payload.name, description=payload.description, change_type=payload.change_type)
    db.add(project)
    db.flush()
    audit_service.write_audit(db, project.id, "project", project.id, "created", detail={"name": project.name})
    db.commit()
    db.refresh(project)
    return project


def list_projects(db: Session) -> list[models.Project]:
    return db.query(models.Project).order_by(models.Project.created_at.desc()).all()


def get_project(db: Session, project_id: int) -> models.Project | None:
    return db.get(models.Project, project_id)


def update_project(db: Session, project: models.Project, payload: ProjectUpdate) -> models.Project:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    db.flush()
    audit_service.write_audit(db, project.id, "project", project.id, "updated")
    db.commit()
    db.refresh(project)
    return project


def delete_project(db: Session, project: models.Project) -> None:
    db.delete(project)
    db.commit()


def build_dashboard(db: Session, project: models.Project) -> ProjectDashboardOut:
    current_analysis = (
        db.query(models.ChangeImpactAnalysisRow)
        .filter_by(project_id=project.id, is_current=True)
        .order_by(models.ChangeImpactAnalysisRow.created_at.desc())
        .first()
    )
    red = amber = green = stakeholder_count = 0
    if current_analysis:
        stakeholders = current_analysis.stakeholder_impacts
        stakeholder_count = len(stakeholders)
        for s in stakeholders:
            if s.heat_rating == "Red":
                red += 1
            elif s.heat_rating == "Amber":
                amber += 1
            elif s.heat_rating == "Green":
                green += 1

    package = project.communication_package
    readiness_score = package.readiness_score if package else None

    top_raid = (
        db.query(models.RaidItemRow)
        .filter(models.RaidItemRow.project_id == project.id, models.RaidItemRow.category == "Risk")
        .filter(models.RaidItemRow.severity.in_(["High", "Critical"]))
        .order_by(models.RaidItemRow.id.desc())
        .limit(3)
        .all()
    )
    open_raid_count = (
        db.query(models.RaidItemRow)
        .filter(models.RaidItemRow.project_id == project.id, models.RaidItemRow.status != "Closed")
        .count()
    )
    document_count = db.query(models.Document).filter_by(project_id=project.id).count()

    return ProjectDashboardOut(
        project=ProjectOut.model_validate(project),
        readiness_score=readiness_score,
        red_count=red,
        amber_count=amber,
        green_count=green,
        stakeholder_count=stakeholder_count,
        top_risks=[r.description for r in top_raid],
        open_raid_count=open_raid_count,
        document_count=document_count,
    )
