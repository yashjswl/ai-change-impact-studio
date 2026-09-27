from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import models
from ..dependencies import get_db
from ..schemas.raid import RaidItemCreate, RaidItemOut, RaidItemUpdate
from ..services import raid_service

router = APIRouter(prefix="/api/v1/projects/{project_id}/raid", tags=["raid"])
item_router = APIRouter(prefix="/api/v1/raid", tags=["raid"])


@router.post("/generate", response_model=list[RaidItemOut])
def generate_raid(project_id: int, db: Session = Depends(get_db)):
    try:
        return raid_service.generate(db, project_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("", response_model=list[RaidItemOut])
def list_raid(project_id: int, db: Session = Depends(get_db)):
    return raid_service.list_items(db, project_id)


@router.post("", response_model=RaidItemOut)
def create_raid_item(project_id: int, payload: RaidItemCreate, db: Session = Depends(get_db)):
    return raid_service.create_item(db, project_id, payload.model_dump())


@item_router.patch("/{item_id}", response_model=RaidItemOut)
def update_raid_item(item_id: int, payload: RaidItemUpdate, db: Session = Depends(get_db)):
    row = db.get(models.RaidItemRow, item_id)
    if not row:
        raise HTTPException(status_code=404, detail="RAID item not found")
    return raid_service.update_item(db, row, payload.model_dump(exclude_unset=True))


@item_router.delete("/{item_id}", status_code=204)
def delete_raid_item(item_id: int, db: Session = Depends(get_db)):
    row = db.get(models.RaidItemRow, item_id)
    if not row:
        raise HTTPException(status_code=404, detail="RAID item not found")
    raid_service.delete_item(db, row)
