from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import models
from ..dependencies import get_db
from ..schemas.comms import (
    ChecklistItemOut,
    ChecklistItemUpdate,
    CommsPlanItemOut,
    CommsPlanItemUpdate,
    CommunicationPackageOut,
)
from ..services import comms_service

router = APIRouter(prefix="/api/v1/projects/{project_id}", tags=["comms"])
item_router = APIRouter(prefix="/api/v1", tags=["comms"])


@router.post("/comms-plan/generate", response_model=list[CommsPlanItemOut])
def generate_comms_plan(project_id: int, db: Session = Depends(get_db)):
    try:
        return comms_service.generate_comms_plan(db, project_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/comms-plan", response_model=list[CommsPlanItemOut])
def list_comms_plan(project_id: int, db: Session = Depends(get_db)):
    return comms_service.list_comms_plan(db, project_id)


@item_router.patch("/comms-plan/{item_id}", response_model=CommsPlanItemOut)
def update_comms_plan_item(item_id: int, payload: CommsPlanItemUpdate, db: Session = Depends(get_db)):
    row = db.get(models.CommsPlanItemRow, item_id)
    if not row:
        raise HTTPException(status_code=404, detail="Comms plan item not found")
    return comms_service.update_comms_plan_item(db, row, payload.model_dump(exclude_unset=True))


@router.post("/communication-package/generate", response_model=CommunicationPackageOut)
def generate_communication_package(project_id: int, db: Session = Depends(get_db)):
    try:
        return comms_service.generate_communication_package(db, project_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/communication-package", response_model=CommunicationPackageOut)
def get_communication_package(project_id: int, db: Session = Depends(get_db)):
    package = comms_service.get_communication_package(db, project_id)
    if not package:
        raise HTTPException(status_code=404, detail="No communication package generated yet")
    return package


@router.get("/checklists", response_model=list[ChecklistItemOut])
def list_checklists(project_id: int, checklist_type: str | None = None, db: Session = Depends(get_db)):
    return comms_service.list_checklist(db, project_id, checklist_type)


@item_router.patch("/checklist-items/{item_id}", response_model=ChecklistItemOut)
def update_checklist_item(item_id: int, payload: ChecklistItemUpdate, db: Session = Depends(get_db)):
    row = db.get(models.ChecklistItemRow, item_id)
    if not row:
        raise HTTPException(status_code=404, detail="Checklist item not found")
    return comms_service.update_checklist_item(db, row, payload.model_dump(exclude_unset=True))
