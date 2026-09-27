# AI Change Impact Studio

A full-stack change management platform modeled on how Big 4 firms (PwC's
"Change Navigator," Prosci ADKAR, standard consulting RACI/RAID practice)
actually run organizational change: a portfolio of change initiatives, each
with an ADKAR-scored stakeholder impact assessment, an Impact × Readiness
heat map, a RACI matrix, a RAID log, a structured communication plan,
narrative communications, a training needs matrix, human-in-the-loop
approvals with a full audit trail, and exportable Word/PowerPoint
deliverables, grounded, where relevant, in your own process documents via
RAG with verified citations.

This supersedes the earlier single-file Streamlit prototype
(`../ai-change-impact-assistant/`, left untouched).

## Stack

- **Backend**: FastAPI + SQLAlchemy 2.0 + SQLite (swap `DATABASE_URL` for
  Postgres later), Google Gemini (`google-genai`) for structured LLM output,
  TF-IDF (scikit-learn) for lightweight RAG, `python-docx` / `python-pptx`
  for exports.
- **Frontend**: React + Vite + TypeScript, Tailwind CSS, Recharts, a custom
  heat map grid component.

## Methodology

- **Prosci ADKAR**: every stakeholder is scored 1–5 on Awareness, Desire,
  Knowledge, Ability, Reinforcement. The **barrier point**, the first
  dimension scoring ≤3, drives the readiness score (barrier-weighted, not a
  naive average), matching how Prosci practitioners actually diagnose
  resistance.
- **Impact × Readiness heat map**: each stakeholder is banded into
  Low/Medium/High on both axes and rated Red/Amber/Green via an explicit
  9-cell lookup table (`backend/app/services/impact_service.py`,
  unit-tested against all 9 cells).
- **RACI** and **RAID** are modeled as first-class, editable entities
  distinct from the stakeholder impact analysis, as they are in real
  consulting practice.
- **Citations are verified, not trusted**: every RAG citation is checked
  against the actual retrieved source text (fuzzy substring match) before
  being shown as "Verified", a known gap in the original prototype, closed
  here (`backend/app/ai/citation_verify.py`).

## Setup

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# get a free key at https://aistudio.google.com/apikey (no card needed)
# edit .env and add your GEMINI_API_KEY
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env   # VITE_API_URL defaults to http://localhost:8000
npm run dev
```

Open http://localhost:5173, create an initiative, and click **Load Sample
Docs** on the Documents tab to try the pre-built onboarding-automation
scenario end to end.

## Project layout

```
backend/
  app/
    main.py                 FastAPI app, router mounts, DB schema creation
    db/models.py             Full SQLAlchemy data model (16 tables)
    schemas/                 API request/response DTOs
    ai/
      llm.py                  Gemini wrapper (structured output, retry/timeout)
      rag.py                  TF-IDF chunking + retrieval
      llm_schemas.py           Pydantic schemas for every LLM generation task
      generation.py            Orchestrates each LLM call
      citation_verify.py       Verifies RAG citations against source text
      prompts.py               System prompts per task
    services/                 Business logic: heat-map formula, persistence,
                               orchestration, one file per domain area
    routers/                  Thin HTTP layer over services/
    exporters/                docx_export.py / pptx_export.py
  tests/                     pytest: heat-map formula (all 9 grid cells),
                             citation verification
  data/sample_docs/          Sample onboarding-automation dataset
frontend/
  src/
    pages/                   One page per domain area (12 pages)
    components/               heatmap/, adkar/, approvals/, export/, ui/
    api/                       Typed REST client + TypeScript types
```

## Verified end-to-end

- Live Gemini-backed impact analysis correctly produces ADKAR scores and the
  barrier-weighted readiness/heat rating (confirmed: editing a stakeholder's
  Desire score live in the UI correctly recomputes the barrier dimension,
  readiness score, and heat color).
- RACI, RAID, communication plan, narrative communications, and training
  matrix all generate correctly from a persisted impact analysis.
- RAG document comparison retrieves real excerpts and every citation is
  verified against the source text before being marked "Verified" in the UI.
- Approvals and audit trail persist correctly and are visible in the UI.
- All three exports (.docx impact assessment, .docx communications, .pptx
  5-slide executive summary) generate, download, and were verified to parse
  correctly with `python-docx` / `python-pptx`.
