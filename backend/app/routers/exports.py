from __future__ import annotations

import os

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ..dependencies import get_db
from ..schemas.export import ExportOut
from ..services import export_service, project_service

router = APIRouter(prefix="/api/v1/projects/{project_id}/exports", tags=["exports"])
download_router = APIRouter(prefix="/api/v1/exports", tags=["exports"])


def _get_project_or_404(db: Session, project_id: int):
    project = project_service.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/docx/impact-onepager", response_model=ExportOut)
def export_impact_onepager(project_id: int, db: Session = Depends(get_db)):
    project = _get_project_or_404(db, project_id)
    try:
        return export_service.export_impact_onepager(db, project)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/docx/comms-package", response_model=ExportOut)
def export_comms_package(project_id: int, db: Session = Depends(get_db)):
    project = _get_project_or_404(db, project_id)
    try:
        return export_service.export_comms_package(db, project)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/pptx/executive-summary", response_model=ExportOut)
def export_executive_summary(project_id: int, db: Session = Depends(get_db)):
    project = _get_project_or_404(db, project_id)
    try:
        return export_service.export_executive_summary(db, project)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@download_router.get("/{export_id}/download")
def download_export(export_id: int, db: Session = Depends(get_db)):
    export = export_service.get_export(db, export_id)
    if not export or not os.path.exists(export.file_path):
        raise HTTPException(status_code=404, detail="Export not found")
    filename = os.path.basename(export.file_path)
    return FileResponse(export.file_path, filename=filename)
