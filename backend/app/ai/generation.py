"""Orchestrates LLM calls for each generation task. Pure functions: given
already-assembled inputs, return a validated schema instance. Persistence and
RAG retrieval live in `services/`, not here."""

from __future__ import annotations

from typing import Optional

from . import llm, prompts
from .llm_schemas import (
    ChangeImpactAnalysis,
    CommunicationPackage,
    CommunicationPlan,
    DocumentDiffAnalysis,
    RaciMatrix,
    RaidLog,
    TrainingNeedsMatrix,
)


def analyze_change(change_description: str, context_block: str = "") -> ChangeImpactAnalysis:
    system = prompts.IMPACT_ANALYSIS_SYSTEM
    user_prompt = f"Business change description:\n{change_description}\n"
    if context_block:
        user_prompt += (
            "\nSupporting context retrieved from uploaded documents "
            "(old process, new process, policies, implementation plan):\n\n"
            f"{context_block}\n"
        )
    user_prompt += "\nProduce a full ChangeImpactAnalysis."
    return llm.call_structured(system=system, user_prompt=user_prompt, schema=ChangeImpactAnalysis, max_tokens=8192)


def generate_communications(analysis_json: str) -> CommunicationPackage:
    user_prompt = (
        "Here is the structured change impact analysis to base all communications on "
        "(JSON):\n\n" + analysis_json + "\n\nProduce a full CommunicationPackage."
    )
    return llm.call_structured(
        system=prompts.COMMUNICATIONS_SYSTEM, user_prompt=user_prompt, schema=CommunicationPackage, max_tokens=8192
    )


def generate_raci(analysis_json: str) -> RaciMatrix:
    user_prompt = (
        "Here is the structured change impact analysis (JSON):\n\n" + analysis_json + "\n\nProduce a full RaciMatrix."
    )
    return llm.call_structured(system=prompts.RACI_SYSTEM, user_prompt=user_prompt, schema=RaciMatrix, max_tokens=4096)


def generate_raid(analysis_json: str) -> RaidLog:
    user_prompt = (
        "Here is the structured change impact analysis (JSON):\n\n" + analysis_json + "\n\nProduce a full RaidLog."
    )
    return llm.call_structured(system=prompts.RAID_SYSTEM, user_prompt=user_prompt, schema=RaidLog, max_tokens=4096)


def generate_comms_plan(analysis_json: str) -> CommunicationPlan:
    user_prompt = (
        "Here is the structured change impact analysis (JSON):\n\n"
        + analysis_json
        + "\n\nProduce a full CommunicationPlan."
    )
    return llm.call_structured(
        system=prompts.COMMS_PLAN_SYSTEM, user_prompt=user_prompt, schema=CommunicationPlan, max_tokens=4096
    )


def generate_training_matrix(analysis_json: str) -> TrainingNeedsMatrix:
    user_prompt = (
        "Here is the structured change impact analysis (JSON):\n\n"
        + analysis_json
        + "\n\nProduce a full TrainingNeedsMatrix."
    )
    return llm.call_structured(
        system=prompts.TRAINING_MATRIX_SYSTEM, user_prompt=user_prompt, schema=TrainingNeedsMatrix, max_tokens=4096
    )


def analyze_document_diff(question: str, context: str) -> DocumentDiffAnalysis:
    user_prompt = (
        f"Question: {question}\n\nRetrieved excerpts:\n\n{context}\n\n"
        "Produce a full DocumentDiffAnalysis grounded only in these excerpts."
    )
    return llm.call_structured(
        system=prompts.DOC_DIFF_SYSTEM, user_prompt=user_prompt, schema=DocumentDiffAnalysis, max_tokens=6144
    )
