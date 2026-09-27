from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..config import SAMPLE_DOCS_DIR
from ..dependencies import get_db
from ..schemas.document import DocumentOut
from ..services import document_service

router = APIRouter(prefix="/api/v1/projects/{project_id}/documents", tags=["documents"])

_SAMPLE_DOC_TYPES = {
    "old_process.md": "old_process",
    "new_process.md": "new_process",
    "company_policies.md": "policy",
    "implementation_plan.md": "implementation_plan",
}


@router.post("", response_model=DocumentOut)
async def upload_document(
    project_id: int,
    doc_type: str = Form("other"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    raw_bytes = await file.read()
    return document_service.add_document(db, project_id, file.filename, doc_type, raw_bytes)


@router.get("", response_model=list[DocumentOut])
def list_documents(project_id: int, db: Session = Depends(get_db)):
    return document_service.list_documents(db, project_id)


@router.post("/load-samples", response_model=list[DocumentOut])
def load_sample_documents(project_id: int, db: Session = Depends(get_db)):
    created = []
    for filename, doc_type in _SAMPLE_DOC_TYPES.items():
        path = SAMPLE_DOCS_DIR / filename
        raw_bytes = path.read_bytes()
        created.append(document_service.add_document(db, project_id, filename, doc_type, raw_bytes))
    return created


@router.delete("/{document_id}", status_code=204)
def delete_document(project_id: int, document_id: int, db: Session = Depends(get_db)):
    doc = document_service.get_document(db, document_id)
    if not doc or doc.project_id != project_id:
        raise HTTPException(status_code=404, detail="Document not found")
    document_service.delete_document(db, doc)
