from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.ai.citation_verify import verify_citation
from app.ai.llm_schemas import Citation, DiffFinding, DocumentDiffAnalysis
from app.ai.rag import chunk_text
from app.db import models
from app.db.base import Base
from app.services import diff_service, document_service


def make_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()


def test_quote_spanning_a_chunk_boundary_is_verified(monkeypatch):
    # 1,500 distinct words so any slice is unambiguous. Chunks are [0, 900) and
    # [750, 1650), so a 270-character quote starting at 690 fits in neither chunk.
    text = " ".join(f"w{i:04d}" for i in range(250))
    quote = text[690:960]
    chunks = chunk_text(text)
    assert not any(quote in c for c in chunks)

    # Documents the defect: concatenated chunks no longer contain the quote.
    assert not verify_citation(quote, "\n".join(chunks))[0]

    db = make_db()
    project = models.Project(name="boundary test")
    db.add(project)
    db.commit()
    document_service.add_document(db, project.id, "old.md", "old_process", text.encode())

    def fake_diff(question, context):
        return DocumentDiffAnalysis(
            summary="s",
            findings=[
                DiffFinding(
                    topic="t",
                    old_state="o",
                    new_state="n",
                    citations=[Citation(source="old.md", excerpt=quote)],
                )
            ],
        )

    monkeypatch.setattr(diff_service.generation, "analyze_document_diff", fake_diff)
    row = diff_service.compare(db, project.id, "what changed?")

    citation = row.findings[0].citations[0]
    assert citation.verified is True


def test_citation_to_an_unknown_document_is_unverified(monkeypatch):
    db = make_db()
    project = models.Project(name="unknown source test")
    db.add(project)
    db.commit()
    document_service.add_document(db, project.id, "old.md", "old_process", b"some real text about refunds")

    def fake_diff(question, context):
        return DocumentDiffAnalysis(
            summary="s",
            findings=[
                DiffFinding(
                    topic="t",
                    old_state="o",
                    new_state="n",
                    citations=[Citation(source="missing.md", excerpt="some real text about refunds")],
                )
            ],
        )

    monkeypatch.setattr(diff_service.generation, "analyze_document_diff", fake_diff)
    row = diff_service.compare(db, project.id, "what changed?")
    assert row.findings[0].citations[0].verified is False
