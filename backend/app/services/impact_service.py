"""Impact analysis generation + persistence, and the heat map formula.

The heat map formula is the analytical core of the product: it turns raw
ADKAR scores into a defensible Red/Amber/Green rating per stakeholder,
following Prosci's "barrier point" logic (the first weak ADKAR dimension
gates progress) rather than a naive average.
"""

from __future__ import annotations

from typing import Literal

from sqlalchemy.orm import Session

from ..ai import generation
from ..ai.llm_schemas import ChangeImpactAnalysis as LlmChangeImpactAnalysis
from ..db import models
from . import audit_service, document_service

ADKAR_DIMENSIONS = ["awareness", "desire", "knowledge", "ability", "reinforcement"]
ADKAR_LABELS = {
    "awareness": "Awareness",
    "desire": "Desire",
    "knowledge": "Knowledge",
    "ability": "Ability",
    "reinforcement": "Reinforcement",
}

HeatRating = Literal["Red", "Amber", "Green"]


def find_barrier_dimension(scores: list[int]) -> tuple[str | None, int | None]:
    """First ADKAR dimension (in A-D-K-A-R order) scoring <= 3. Returns
    (dimension_label, score) or (None, None) if no dimension is a barrier."""
    for dim, score in zip(ADKAR_DIMENSIONS, scores):
        if score <= 3:
            return ADKAR_LABELS[dim], score
    return None, None


def compute_readiness_score(scores: list[int]) -> float:
    """0-100. Barrier-weighted: a low early dimension caps the score even if
    later dimensions are strong, per Prosci's sequential-barrier logic."""
    avg = sum(scores) / len(scores)
    _, barrier_score = find_barrier_dimension(scores)
    if barrier_score is not None:
        raw = 0.65 * barrier_score + 0.35 * avg
    else:
        raw = avg
    return round(raw / 5 * 100, 1)


def compute_impact_score(impact_severity: int) -> float:
    return round(impact_severity / 5 * 100, 1)


def _band(score: float) -> Literal["Low", "Medium", "High"]:
    if score <= 33:
        return "Low"
    if score <= 66:
        return "Medium"
    return "High"


_HEAT_TABLE: dict[tuple[str, str], HeatRating] = {
    ("High", "Low"): "Red",
    ("High", "Medium"): "Red",
    ("High", "High"): "Amber",
    ("Medium", "Low"): "Red",
    ("Medium", "Medium"): "Amber",
    ("Medium", "High"): "Green",
    ("Low", "Low"): "Amber",
    ("Low", "Medium"): "Green",
    ("Low", "High"): "Green",
}


def compute_heat_rating(impact_score: float, readiness_score: float) -> HeatRating:
    return _HEAT_TABLE[(_band(impact_score), _band(readiness_score))]


def apply_scores(row: models.StakeholderImpactRow) -> None:
    """Recomputes and caches readiness_score/impact_score/heat_rating/barrier
    on a StakeholderImpactRow from its current ADKAR + severity fields."""
    scores = [
        row.adkar_awareness,
        row.adkar_desire,
        row.adkar_knowledge,
        row.adkar_ability,
        row.adkar_reinforcement,
    ]
    barrier_label, _ = find_barrier_dimension(scores)
    row.adkar_barrier_dimension = barrier_label
    row.readiness_score = compute_readiness_score(scores)
    row.impact_score = compute_impact_score(row.impact_severity)
    row.heat_rating = compute_heat_rating(row.impact_score, row.readiness_score)


def generate_and_persist_analysis(
    db: Session, project_id: int, change_description: str, ground_in_documents: bool = True
) -> models.ChangeImpactAnalysisRow:
    context_block = ""
    if ground_in_documents:
        store = document_service.build_document_store(db, project_id)
        if store.chunks:
            chunks = store.search(change_description, top_k=8)
            if chunks:
                context_block = store.format_context(chunks)

    result: LlmChangeImpactAnalysis = generation.analyze_change(change_description, context_block=context_block)

    db.query(models.ChangeImpactAnalysisRow).filter_by(project_id=project_id, is_current=True).update(
        {"is_current": False}
    )

    analysis = models.ChangeImpactAnalysisRow(
        project_id=project_id,
        change_title=result.change_title,
        change_summary=result.change_summary,
        overall_risks=result.overall_risks,
        success_factors=result.success_factors,
        is_current=True,
    )
    db.add(analysis)
    db.flush()

    for s in result.stakeholder_impacts:
        row = models.StakeholderImpactRow(
            analysis_id=analysis.id,
            stakeholder=s.stakeholder,
            what_changes=s.what_changes,
            what_is_impacted=s.what_is_impacted,
            what_to_learn=s.what_to_learn,
            resistance_risk=s.resistance_risk,
            action_required=s.action_required,
            impact_type=s.impact_type,
            impact_severity=s.impact_severity,
            adkar_awareness=s.adkar.awareness,
            adkar_desire=s.adkar.desire,
            adkar_knowledge=s.adkar.knowledge,
            adkar_ability=s.adkar.ability,
            adkar_reinforcement=s.adkar.reinforcement,
            adkar_rationale=s.adkar.rationale,
        )
        apply_scores(row)
        db.add(row)

    audit_service.write_audit(
        db, project_id, "impact_analysis", analysis.id, "generated", detail={"change_title": result.change_title}
    )
    db.commit()
    db.refresh(analysis)
    return analysis


def get_current_analysis(db: Session, project_id: int) -> models.ChangeImpactAnalysisRow | None:
    return (
        db.query(models.ChangeImpactAnalysisRow)
        .filter_by(project_id=project_id, is_current=True)
        .order_by(models.ChangeImpactAnalysisRow.created_at.desc())
        .first()
    )


def update_stakeholder(db: Session, row: models.StakeholderImpactRow, updates: dict) -> models.StakeholderImpactRow:
    for field, value in updates.items():
        setattr(row, field, value)
    row.edited_by_human = True
    apply_scores(row)
    db.flush()
    audit_service.write_audit(
        db, row.analysis.project_id, "stakeholder_impact", row.id, "updated", detail={"fields": list(updates.keys())}
    )
    db.commit()
    db.refresh(row)
    return row


def analysis_to_json(analysis: models.ChangeImpactAnalysisRow) -> str:
    """Serializes a persisted analysis back into the JSON shape downstream
    generators (RACI/RAID/comms/training) expect as grounding context."""
    import json

    return json.dumps(
        {
            "change_title": analysis.change_title,
            "change_summary": analysis.change_summary,
            "overall_risks": analysis.overall_risks,
            "success_factors": analysis.success_factors,
            "stakeholder_impacts": [
                {
                    "stakeholder": s.stakeholder,
                    "what_changes": s.what_changes,
                    "what_is_impacted": s.what_is_impacted,
                    "what_to_learn": s.what_to_learn,
                    "resistance_risk": s.resistance_risk,
                    "action_required": s.action_required,
                    "impact_type": s.impact_type,
                    "impact_severity": s.impact_severity,
                    "heat_rating": s.heat_rating,
                    "adkar_barrier_dimension": s.adkar_barrier_dimension,
                }
                for s in analysis.stakeholder_impacts
            ],
        },
        indent=2,
    )
