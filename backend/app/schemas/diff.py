from __future__ import annotations

import datetime

from pydantic import BaseModel, ConfigDict


class DiffRequest(BaseModel):
    question: str = "What changed between the old and new processes?"


class CitationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source: str
    excerpt: str
    verified: bool
    verification_note: str | None


class DiffFindingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    topic: str
    old_state: str
    new_state: str
    citations: list[CitationOut]


class DocumentDiffAnalysisOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    question: str
    summary: str
    created_at: datetime.datetime
    findings: list[DiffFindingOut]
