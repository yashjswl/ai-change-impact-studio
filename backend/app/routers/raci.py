from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import models
from ..dependencies import get_db
from ..schemas.raci import RaciItemCreate, RaciItemOut, RaciItemUpdate
from ..services import raci_service

router = APIRouter(prefix="/api/v1/projects/{project_id}/raci", tags=["raci"])
item_router = APIRouter(prefix="/api/v1/raci", tags=["raci"])


@router.post("/generate", response_model=list[RaciItemOut])
def generate_raci(project_id: int, db: Session = Depends(get_db)):
    try:
        return raci_service.generate(db, project_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("", response_model=list[RaciItemOut])
def list_raci(project_id: int, db: Session = Depends(get_db)):
    return raci_service.list_items(db, project_id)


@router.post("", response_model=RaciItemOut)
def create_raci_item(project_id: int, payload: RaciItemCreate, db: Session = Depends(get_db)):
    return raci_service.create_item(db, project_id, payload.model_dump())


@item_router.patch("/{item_id}", response_model=RaciItemOut)
def update_raci_item(item_id: int, payload: RaciItemUpdate, db: Session = Depends(get_db)):
    row = db.get(models.RaciItemRow, item_id)
    if not row:
        raise HTTPException(status_code=404, detail="RACI item not found")
    return raci_service.update_item(db, row, payload.model_dump(exclude_unset=True))


@item_router.delete("/{item_id}", status_code=204)
def delete_raci_item(item_id: int, db: Session = Depends(get_db)):
    row = db.get(models.RaciItemRow, item_id)
    if not row:
        raise HTTPException(status_code=404, detail="RACI item not found")
    raci_service.delete_item(db, row)
