from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..dependencies import get_db
from ..schemas.project import ProjectCreate, ProjectDashboardOut, ProjectOut, ProjectUpdate
from ..services import project_service

router = APIRouter(prefix="/api/v1/projects", tags=["projects"])


def _get_or_404(db: Session, project_id: int):
    project = project_service.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("", response_model=ProjectOut)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    return project_service.create_project(db, payload)


@router.get("", response_model=list[ProjectOut])
def list_projects(db: Session = Depends(get_db)):
    return project_service.list_projects(db)


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, project_id)


@router.patch("/{project_id}", response_model=ProjectOut)
def update_project(project_id: int, payload: ProjectUpdate, db: Session = Depends(get_db)):
    project = _get_or_404(db, project_id)
    return project_service.update_project(db, project, payload)


@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = _get_or_404(db, project_id)
    project_service.delete_project(db, project)


@router.get("/{project_id}/dashboard", response_model=ProjectDashboardOut)
def get_dashboard(project_id: int, db: Session = Depends(get_db)):
    project = _get_or_404(db, project_id)
    return project_service.build_dashboard(db, project)


portfolio_router = APIRouter(prefix="/api/v1/portfolio", tags=["portfolio"])


@portfolio_router.get("", response_model=list[ProjectDashboardOut])
def get_portfolio(db: Session = Depends(get_db)):
    return [project_service.build_dashboard(db, p) for p in project_service.list_projects(db)]
