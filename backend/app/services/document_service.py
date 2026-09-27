from __future__ import annotations

from sqlalchemy.orm import Session

from ..ai import ingest
from ..ai.rag import Chunk, DocumentStore, chunk_text
from ..db import models
from . import audit_service


def add_document(db: Session, project_id: int, filename: str, doc_type: str, raw_bytes: bytes) -> models.Document:
    text = ingest.extract_text(filename, raw_bytes)
    doc = models.Document(
        project_id=project_id,
        filename=filename,
        doc_type=doc_type,
        raw_text=text,
        char_count=len(text),
    )
    db.add(doc)
    db.flush()

    for i, piece in enumerate(chunk_text(text)):
        db.add(models.DocChunk(document_id=doc.id, chunk_index=i, text=piece))

    audit_service.write_audit(
        db, project_id, "document", doc.id, "created", detail={"filename": filename, "doc_type": doc_type}
    )
    db.commit()
    db.refresh(doc)
    return doc


def list_documents(db: Session, project_id: int) -> list[models.Document]:
    return db.query(models.Document).filter_by(project_id=project_id).order_by(models.Document.uploaded_at).all()


def get_document(db: Session, document_id: int) -> models.Document | None:
    return db.get(models.Document, document_id)


def delete_document(db: Session, doc: models.Document) -> None:
    db.delete(doc)
    db.commit()


def build_document_store(db: Session, project_id: int) -> DocumentStore:
    """Rebuilds an in-memory TF-IDF index from persisted chunks. Cheap enough
    (a handful of small documents per project) to do on every query rather
    than maintaining a separate cached index."""
    store = DocumentStore()
    documents = list_documents(db, project_id)
    for doc in documents:
        chunks = (
            db.query(models.DocChunk)
            .filter_by(document_id=doc.id)
            .order_by(models.DocChunk.chunk_index)
            .all()
        )
        for chunk in chunks:
            store.chunks.append(
                Chunk(doc_name=doc.filename, doc_type=doc.doc_type, chunk_id=chunk.chunk_index, text=chunk.text)
            )
    store._invalidate()
    return store
