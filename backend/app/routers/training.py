from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import models
from ..dependencies import get_db
from ..schemas.training import TrainingItemCreate, TrainingItemOut, TrainingItemUpdate
from ..services import training_service

router = APIRouter(prefix="/api/v1/projects/{project_id}/training-matrix", tags=["training"])
item_router = APIRouter(prefix="/api/v1/training-matrix", tags=["training"])


@router.post("/generate", response_model=list[TrainingItemOut])
def generate_training_matrix(project_id: int, db: Session = Depends(get_db)):
    try:
        return training_service.generate(db, project_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("", response_model=list[TrainingItemOut])
def list_training_matrix(project_id: int, db: Session = Depends(get_db)):
    return training_service.list_items(db, project_id)


@router.post("", response_model=TrainingItemOut)
def create_training_item(project_id: int, payload: TrainingItemCreate, db: Session = Depends(get_db)):
    return training_service.create_item(db, project_id, payload.model_dump())


@item_router.patch("/{item_id}", response_model=TrainingItemOut)
def update_training_item(item_id: int, payload: TrainingItemUpdate, db: Session = Depends(get_db)):
    row = db.get(models.TrainingMatrixItemRow, item_id)
    if not row:
        raise HTTPException(status_code=404, detail="Training item not found")
    return training_service.update_item(db, row, payload.model_dump(exclude_unset=True))


@item_router.delete("/{item_id}", status_code=204)
def delete_training_item(item_id: int, db: Session = Depends(get_db)):
    row = db.get(models.TrainingMatrixItemRow, item_id)
    if not row:
        raise HTTPException(status_code=404, detail="Training item not found")
    training_service.delete_item(db, row)
