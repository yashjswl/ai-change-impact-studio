from __future__ import annotations

from sqlalchemy.orm import Session

from ..ai import generation
from ..ai.citation_verify import verify_citation
from ..ai.rag import Chunk, DocumentStore
from ..db import models
from . import audit_service, document_service

# A "what changed" question shares little vocabulary with the documents, so
# retrieval hands the model only part of each one. Measured in backend/eval:
# on small corpora, retrieval put under half the chunks in context and recall of
# known changes was 0.55, versus 0.91 with the full documents. Below this size
# the whole project is passed to the model; above it, retrieval takes over.
FULL_CONTEXT_MAX_CHUNKS = 40
RETRIEVAL_TOP_K = 10


def select_context_chunks(store: DocumentStore, question: str) -> list[Chunk]:
    if len(store.chunks) <= FULL_CONTEXT_MAX_CHUNKS:
        return list(store.chunks)
    return store.search(question, top_k=RETRIEVAL_TOP_K)


def compare(db: Session, project_id: int, question: str) -> models.DocumentDiffAnalysisRow:
    store = document_service.build_document_store(db, project_id)
    if not store.chunks:
        raise ValueError(
            "No documents loaded for this project. Upload old/new process docs "
            "(and optionally policies / implementation plan) first."
        )
    chunks = select_context_chunks(store, question)
    if not chunks:
        raise ValueError("No relevant content found in the uploaded documents for this question.")

    context = store.format_context(chunks)
    # Verify citations against each cited document's full text. Chunks overlap by
    # only 150 characters, so a quote longer than that can straddle a chunk
    # boundary and fail to match when chunks are simply concatenated (measured in
    # backend/eval: 3 of 5 rejected real quotes were this artifact).
    source_text_by_doc = {d.filename: d.raw_text for d in document_service.list_documents(db, project_id)}

    result = generation.analyze_document_diff(question, context)

    diff_row = models.DocumentDiffAnalysisRow(project_id=project_id, question=question, summary=result.summary)
    db.add(diff_row)
    db.flush()

    for finding in result.findings:
        finding_row = models.DiffFindingRow(
            diff_analysis_id=diff_row.id,
            topic=finding.topic,
            old_state=finding.old_state,
            new_state=finding.new_state,
        )
        db.add(finding_row)
        db.flush()

        for citation in finding.citations:
            source_text = source_text_by_doc.get(citation.source, "")
            verified, note = verify_citation(citation.excerpt, source_text)
            db.add(
                models.CitationRow(
                    finding_id=finding_row.id,
                    source=citation.source,
                    excerpt=citation.excerpt,
                    verified=verified,
                    verification_note=note,
                )
            )

    audit_service.write_audit(
        db, project_id, "document_diff", diff_row.id, "generated", detail={"question": question}
    )
    db.commit()
    db.refresh(diff_row)
    return diff_row


def list_diffs(db: Session, project_id: int) -> list[models.DocumentDiffAnalysisRow]:
    return (
        db.query(models.DocumentDiffAnalysisRow)
        .filter_by(project_id=project_id)
        .order_by(models.DocumentDiffAnalysisRow.created_at.desc())
        .all()
    )
