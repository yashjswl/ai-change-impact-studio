"""SQLAlchemy ORM models, the full data model for the studio.

Status/category fields are plain strings (validated at the API/schema layer)
rather than DB-level enums, so new values (e.g. a new RAID category) don't
require a migration, a deliberate tradeoff for an early-stage tool on
SQLite. All child tables cascade-delete with their project.
"""

from __future__ import annotations

import datetime
from typing import List, Optional

from sqlalchemy import JSON, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    change_type: Mapped[str] = mapped_column(default="Process")
    status: Mapped[str] = mapped_column(default="active")
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    documents: Mapped[List["Document"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    analyses: Mapped[List["ChangeImpactAnalysisRow"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    raci_items: Mapped[List["RaciItemRow"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    raid_items: Mapped[List["RaidItemRow"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    comms_plan_items: Mapped[List["CommsPlanItemRow"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    communication_package: Mapped[Optional["CommunicationPackageRow"]] = relationship(
        back_populates="project", cascade="all, delete-orphan", uselist=False
    )
    checklist_items: Mapped[List["ChecklistItemRow"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    training_items: Mapped[List["TrainingMatrixItemRow"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    diff_analyses: Mapped[List["DocumentDiffAnalysisRow"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    approvals: Mapped[List["Approval"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    audit_logs: Mapped[List["AuditLog"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    exports: Mapped[List["Export"]] = relationship(back_populates="project", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    filename: Mapped[str] = mapped_column(nullable=False)
    doc_type: Mapped[str] = mapped_column(default="other")
    raw_text: Mapped[str] = mapped_column(Text, default="")
    char_count: Mapped[int] = mapped_column(default=0)
    uploaded_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())

    project: Mapped["Project"] = relationship(back_populates="documents")
    chunks: Mapped[List["DocChunk"]] = relationship(back_populates="document", cascade="all, delete-orphan")


class DocChunk(Base):
    __tablename__ = "doc_chunks"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), index=True)
    chunk_index: Mapped[int] = mapped_column(default=0)
    text: Mapped[str] = mapped_column(Text, default="")

    document: Mapped["Document"] = relationship(back_populates="chunks")


class ChangeImpactAnalysisRow(Base):
    __tablename__ = "change_impact_analyses"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    change_title: Mapped[str] = mapped_column(default="")
    change_summary: Mapped[str] = mapped_column(Text, default="")
    overall_risks: Mapped[list] = mapped_column(JSON, default=list)
    success_factors: Mapped[list] = mapped_column(JSON, default=list)
    is_current: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())

    project: Mapped["Project"] = relationship(back_populates="analyses")
    stakeholder_impacts: Mapped[List["StakeholderImpactRow"]] = relationship(
        back_populates="analysis", cascade="all, delete-orphan"
    )


class StakeholderImpactRow(Base):
    __tablename__ = "stakeholder_impacts"

    id: Mapped[int] = mapped_column(primary_key=True)
    analysis_id: Mapped[int] = mapped_column(
        ForeignKey("change_impact_analyses.id", ondelete="CASCADE"), index=True
    )
    stakeholder: Mapped[str] = mapped_column(default="")
    what_changes: Mapped[str] = mapped_column(Text, default="")
    what_is_impacted: Mapped[list] = mapped_column(JSON, default=list)
    what_to_learn: Mapped[list] = mapped_column(JSON, default=list)
    resistance_risk: Mapped[list] = mapped_column(JSON, default=list)
    action_required: Mapped[list] = mapped_column(JSON, default=list)
    impact_type: Mapped[list] = mapped_column(JSON, default=list)
    impact_severity: Mapped[int] = mapped_column(default=3)

    adkar_awareness: Mapped[int] = mapped_column(default=3)
    adkar_desire: Mapped[int] = mapped_column(default=3)
    adkar_knowledge: Mapped[int] = mapped_column(default=3)
    adkar_ability: Mapped[int] = mapped_column(default=3)
    adkar_reinforcement: Mapped[int] = mapped_column(default=3)
    adkar_barrier_dimension: Mapped[Optional[str]] = mapped_column(nullable=True)
    adkar_rationale: Mapped[str] = mapped_column(Text, default="")

    readiness_score: Mapped[float] = mapped_column(default=0.0)
    impact_score: Mapped[float] = mapped_column(default=0.0)
    heat_rating: Mapped[str] = mapped_column(default="Amber")

    edited_by_human: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    analysis: Mapped["ChangeImpactAnalysisRow"] = relationship(back_populates="stakeholder_impacts")


class RaciItemRow(Base):
    __tablename__ = "raci_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    workstream: Mapped[str] = mapped_column(default="")
    activity: Mapped[str] = mapped_column(default="")
    responsible: Mapped[str] = mapped_column(default="")
    accountable: Mapped[str] = mapped_column(default="")
    consulted: Mapped[str] = mapped_column(default="")
    informed: Mapped[str] = mapped_column(default="")
    order_index: Mapped[int] = mapped_column(default=0)

    project: Mapped["Project"] = relationship(back_populates="raci_items")


class RaidItemRow(Base):
    __tablename__ = "raid_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    category: Mapped[str] = mapped_column(default="Risk")
    description: Mapped[str] = mapped_column(Text, default="")
    severity: Mapped[str] = mapped_column(default="Medium")
    likelihood: Mapped[str] = mapped_column(default="Medium")
    owner: Mapped[str] = mapped_column(default="")
    status: Mapped[str] = mapped_column(default="Open")
    mitigation: Mapped[str] = mapped_column(Text, default="")
    due_date: Mapped[Optional[str]] = mapped_column(nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    project: Mapped["Project"] = relationship(back_populates="raid_items")


class CommsPlanItemRow(Base):
    __tablename__ = "comms_plan_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    audience: Mapped[str] = mapped_column(default="")
    key_message: Mapped[str] = mapped_column(Text, default="")
    channel: Mapped[str] = mapped_column(default="")
    owner: Mapped[str] = mapped_column(default="")
    timing: Mapped[str] = mapped_column(default="")
    order_index: Mapped[int] = mapped_column(default=0)

    project: Mapped["Project"] = relationship(back_populates="comms_plan_items")


class CommunicationPackageRow(Base):
    __tablename__ = "communication_packages"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), unique=True, index=True
    )
    employee_subject: Mapped[str] = mapped_column(default="")
    employee_body: Mapped[str] = mapped_column(Text, default="")
    manager_subject: Mapped[str] = mapped_column(default="")
    manager_body: Mapped[str] = mapped_column(Text, default="")
    manager_talking_points: Mapped[list] = mapped_column(JSON, default=list)
    faq: Mapped[list] = mapped_column(JSON, default=list)
    readiness_score: Mapped[int] = mapped_column(default=0)
    readiness_rationale: Mapped[str] = mapped_column(Text, default="")
    readiness_top_risks: Mapped[list] = mapped_column(JSON, default=list)
    readiness_next_steps: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())

    project: Mapped["Project"] = relationship(back_populates="communication_package")


class ChecklistItemRow(Base):
    __tablename__ = "checklist_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    checklist_type: Mapped[str] = mapped_column(default="training")
    item: Mapped[str] = mapped_column(Text, default="")
    owner: Mapped[str] = mapped_column(default="")
    due: Mapped[Optional[str]] = mapped_column(nullable=True)
    is_done: Mapped[bool] = mapped_column(default=False)
    order_index: Mapped[int] = mapped_column(default=0)

    project: Mapped["Project"] = relationship(back_populates="checklist_items")


class TrainingMatrixItemRow(Base):
    __tablename__ = "training_matrix_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    role: Mapped[str] = mapped_column(default="")
    current_capability: Mapped[str] = mapped_column(Text, default="")
    required_capability: Mapped[str] = mapped_column(Text, default="")
    gap: Mapped[str] = mapped_column(Text, default="")
    training_action: Mapped[str] = mapped_column(Text, default="")
    owner: Mapped[str] = mapped_column(default="")
    due_date: Mapped[Optional[str]] = mapped_column(nullable=True)
    priority: Mapped[str] = mapped_column(default="Medium")

    project: Mapped["Project"] = relationship(back_populates="training_items")


class DocumentDiffAnalysisRow(Base):
    __tablename__ = "document_diff_analyses"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    question: Mapped[str] = mapped_column(Text, default="")
    summary: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())

    project: Mapped["Project"] = relationship(back_populates="diff_analyses")
    findings: Mapped[List["DiffFindingRow"]] = relationship(back_populates="diff_analysis", cascade="all, delete-orphan")


class DiffFindingRow(Base):
    __tablename__ = "diff_findings"

    id: Mapped[int] = mapped_column(primary_key=True)
    diff_analysis_id: Mapped[int] = mapped_column(
        ForeignKey("document_diff_analyses.id", ondelete="CASCADE"), index=True
    )
    topic: Mapped[str] = mapped_column(default="")
    old_state: Mapped[str] = mapped_column(Text, default="")
    new_state: Mapped[str] = mapped_column(Text, default="")

    diff_analysis: Mapped["DocumentDiffAnalysisRow"] = relationship(back_populates="findings")
    citations: Mapped[List["CitationRow"]] = relationship(back_populates="finding", cascade="all, delete-orphan")


class CitationRow(Base):
    __tablename__ = "citations"

    id: Mapped[int] = mapped_column(primary_key=True)
    finding_id: Mapped[int] = mapped_column(ForeignKey("diff_findings.id", ondelete="CASCADE"), index=True)
    source: Mapped[str] = mapped_column(default="")
    excerpt: Mapped[str] = mapped_column(Text, default="")
    verified: Mapped[bool] = mapped_column(default=False)
    verification_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    finding: Mapped["DiffFindingRow"] = relationship(back_populates="citations")


class Approval(Base):
    __tablename__ = "approvals"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    artifact_type: Mapped[str] = mapped_column(index=True)
    artifact_id: Mapped[int] = mapped_column(index=True)
    reviewer_name: Mapped[str] = mapped_column(default="")
    status: Mapped[str] = mapped_column(default="pending")
    comments: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())

    project: Mapped["Project"] = relationship(back_populates="approvals")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=True, index=True
    )
    entity_type: Mapped[str] = mapped_column(default="")
    entity_id: Mapped[Optional[int]] = mapped_column(nullable=True)
    action: Mapped[str] = mapped_column(default="")
    actor: Mapped[str] = mapped_column(default="system")
    detail: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())

    project: Mapped["Project"] = relationship(back_populates="audit_logs")


class Export(Base):
    __tablename__ = "exports"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    export_type: Mapped[str] = mapped_column(default="")
    file_path: Mapped[str] = mapped_column(default="")
    generated_by: Mapped[str] = mapped_column(default="system")
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())

    project: Mapped["Project"] = relationship(back_populates="exports")
