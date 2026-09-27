"""Seeds a sample initiative on first boot so a fresh database (e.g. a
Render free-tier instance that just reset) isn't a blank slate. Only ever
creates data when the projects table is empty, so it never overwrites or
duplicates anything a real user has created."""

from __future__ import annotations

from sqlalchemy.orm import Session

from ..config import SAMPLE_DOCS_DIR
from ..db import models
from . import document_service

SAMPLE_PROJECT_NAME = "Employee Onboarding Automation (Sample)"
SAMPLE_PROJECT_DESCRIPTION = "Moving from manual to automated onboarding"

_SAMPLE_DOC_TYPES = {
    "old_process.md": "old_process",
    "new_process.md": "new_process",
    "company_policies.md": "policy",
    "implementation_plan.md": "implementation_plan",
}


def seed_sample_project_if_empty(db: Session) -> None:
    if db.query(models.Project).count() > 0:
        return

    project = models.Project(
        name=SAMPLE_PROJECT_NAME,
        description=SAMPLE_PROJECT_DESCRIPTION,
        change_type="Process",
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    for filename, doc_type in _SAMPLE_DOC_TYPES.items():
        raw_bytes = (SAMPLE_DOCS_DIR / filename).read_bytes()
        document_service.add_document(db, project.id, filename, doc_type, raw_bytes)
