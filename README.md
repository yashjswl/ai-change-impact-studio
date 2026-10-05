# AI Change Impact Studio

A full-stack Python application for organizational change management, built to model how impact assessments, stakeholder analysis, and change communications are actually produced in consulting practice, rather than as a generic LLM demo.

Given a description of a business process change, the system generates a stakeholder impact assessment scored against the Prosci ADKAR model, a Red/Amber/Green readiness heat map, a RACI matrix, a RAID log, a structured communication plan, a training needs matrix, and exportable Word and PowerPoint deliverables. It also supports retrieval-augmented generation over uploaded process documentation, so a user can ask what changed between an old and a new process and receive a cited, independently verified answer.

## Live demo

- Application: https://p1.yashjswl.com
- API: https://ai-change-impact-studio-api.onrender.com/health

The backend is hosted on Render's free tier, which spins down after inactivity, so the first request after a period of idleness can take up to a minute while it restarts.

## Screenshots

**Portfolio.** Every initiative with its readiness score, stakeholder risk counts, and open RAID items.

![Portfolio dashboard](docs/screenshots/01-portfolio.png)

**Impact assessment with ADKAR scoring.** LLM-drafted stakeholder analysis grounded in the uploaded documents. ADKAR scores are editable, and the barrier point, readiness score, and heat rating recompute on every change.

![Impact assessment and ADKAR scoring](docs/screenshots/03-impact-adkar.png)

**Readiness heat map.** Stakeholders plotted by impact against readiness and rated Red, Amber, or Green.

![Readiness heat map](docs/screenshots/02-heatmap.png)

**Communication plan.** A structured plan by audience, message, channel, owner, and timing, generated from the impact analysis.

![Communication plan](docs/screenshots/04-communications.png)

**Document comparison with citation verification.** A comparison of old and new process documents grounded in the uploaded text. Each citation is checked against the cited document, so a paraphrased or altered excerpt is flagged as unverified rather than accepted.

![Document comparison](docs/screenshots/05-document-comparison.png)

## Core technical focus

The backend is written entirely in Python, and the architecture is organized around two problems central to production LLM systems: structured output and retrieval-augmented generation.

**Structured LLM output.** Every generation task, impact analysis, RACI, RAID, communications, training matrices, document comparison, is implemented as a structured output call to Google Gemini, using Pydantic schemas as the response contract (`backend/app/ai/llm_schemas.py`). The LLM client includes retry logic and request timeouts for production reliability.

**Retrieval-augmented generation.** Uploaded documents are chunked and indexed with TF-IDF (`backend/app/ai/rag.py`), which avoids the overhead of an embedding model for a small, per-project document set. For projects of up to 40 chunks the model receives the full documents, because measurement showed retrieval dropping evidence on the document-comparison task (see Evaluation). Larger projects fall back to top-10 retrieval. Every citation the model returns is independently checked against the cited document (`backend/app/ai/citation_verify.py`), by aligning words within a sliding window and requiring every number to match, before the UI labels it as verified.

## Readiness scoring model

Each stakeholder is scored across the five Prosci ADKAR dimensions: Awareness, Desire, Knowledge, Ability, and Reinforcement. Prosci's methodology treats readiness as gated by the weakest dimension rather than as an average, since a stakeholder cannot demonstrate Ability without first having Desire. `backend/app/services/impact_service.py` identifies the first ADKAR dimension scoring 3 or below as the barrier point and weights the readiness score 65/35 toward that barrier over the raw average. Readiness and an LLM-assigned impact severity are then banded into a 3x3 grid and mapped to a Red, Amber, or Green rating through an explicit lookup table, which is unit tested against all nine grid cells.

## Evaluation

The retrieval, citation verification and document-comparison parts are measured on a labeled evaluation set in [`backend/eval`](backend/eval): 12 documents (35 chunks), 42 questions with evidence-span labels, and 74 labeled citations. Variants were compared on a dev split and the held-out test split was run once, with the adoption rule fixed beforehand. Intervals are 95%. Every number below is generated from the committed result files by `python -m eval.report`; method and reproduction steps are in [`backend/eval/README.md`](backend/eval/README.md). ADKAR scoring is not evaluated, because it is an LLM judgment with no ground truth.

### Retrieval

Held-out test split: 26 questions over 35 chunks from 12 documents.

| Retriever | hit@1 | hit@3 | hit@5 | MRR@10 |
|---|---|---|---|---|
| Random ranking (expected) | 0.04 | 0.11 | 0.18 | n/a |
| TF-IDF (shipped) | 0.65 (0.46 to 0.81) | 0.88 (0.71 to 0.96) | 0.96 (0.81 to 0.99) | 0.78 (0.65 to 0.90) |
| TF-IDF + stemming | 0.62 (0.43 to 0.78) | 0.92 (0.76 to 0.98) | 0.96 (0.81 to 0.99) | 0.75 (0.62 to 0.88) |
| BM25 | 0.69 (0.50 to 0.83) | 0.85 (0.66 to 0.94) | 0.92 (0.76 to 0.98) | 0.79 (0.66 to 0.91) |
| BM25 + stemming | 0.69 (0.50 to 0.83) | 0.88 (0.71 to 0.96) | 0.96 (0.81 to 0.99) | 0.79 (0.66 to 0.91) |
| Gemini embeddings | 0.65 (0.46 to 0.81) | 0.96 (0.81 to 0.99) | 1.00 (0.87 to 1.00) | 0.79 (0.67 to 0.90) |

No alternative was reliably better than the shipped TF-IDF. Compared on the same questions, every paired difference in MRR@10 had an interval spanning zero (stemming: -0.03, -0.13 to +0.06). Stemming looked helpful on the dev split (MRR@10 +0.14) and that did not replicate on the test split, so retrieval was left unchanged rather than adding complexity the data does not support.

### Citation verification

Held-out test split: 37 labeled citations (15 valid, 22 invalid), threshold 0.85. Invalid cases include fabricated text, text from the wrong document, paraphrases, and real sentences with one number changed.

| Verifier | Precision | Recall | F1 | Altered numbers accepted |
|---|---|---|---|---|
| Character-level, longest block (originally shipped) | 1.00 | 0.60 | 0.75 | 0 of 5 |
| Same, with difflib autojunk disabled | 0.91 | 0.67 | 0.77 | 1 of 5 |
| Word-level window, numbers not checked | 0.75 | 1.00 | 0.86 | 5 of 5 |
| Word-level window, numbers must match (current) | 1.00 | 1.00 | 1.00 | 0 of 5 |

The evaluation found four defects, each now fixed and covered by a regression test:

- difflib's default `autojunk` collapses the fuzzy match on documents over 200 characters, scoring near-verbatim quotes at 1 to 4% overlap.
- A single edited word split the longest matching block, so lightly edited quotes were rejected (recall 0.60).
- My first fix, a tolerant word-level matcher, accepted every citation whose only difference was an altered number, such as "$75" quoted as "$85". Numbers must now match exactly.
- The service verified against concatenated chunks, which overlap by only 150 characters. Quotes longer than that were wrongly rejected, 3 of the 5 rejections in one live run. It now verifies against the cited document's text.

The perfect score on the labeled cases should be read with care: they were built to probe these specific behaviors and are easier than real model errors.

### Document comparison, end to end

Real `gemini-flash-lite-latest` output, 15 runs per row (5 scenarios x 3 runs), scored against the known changes in each document pair.

| Context given to the model | Chunks in context | Known changes with evidence present | Findings returned | Recall of known changes | Runs failed |
|---|---|---|---|---|---|
| Retrieval only (previous behavior) | 2.8 of 6.2 | 72% | 3.9 | 0.52 | 0 of 15 |
| Full documents (now used for small corpora) | 6.2 of 6.2 | 100% | 7.7 | 0.93 | 0 of 15 |

Recall improved in four of the five scenarios (expense 0.29 to 0.83, vendor 0.43 to 1.00, incident 0.48 to 1.00, refund 0.48 to 0.90) and was slightly lower for onboarding (0.93 to 0.89). The question "what changed" shares little vocabulary with the documents, so retrieval handed the model fewer than half the chunks and the model could not report changes it never saw. For corpora of up to 40 chunks the service now passes the whole documents; the cost is about 2.3 seconds of added latency per request (2.9 to 5.2 seconds on average).

On real output the model's citations were accepted 98.4% of the time by the word-level verifier and 96.4% by the character-level one (252 citations); the model mostly quotes accurately, so the labeled test above is where the verifiers differ.

### Limitations

The corpus is synthetic and was written with LLM assistance, so it is not real enterprise documentation, and its questions share more vocabulary with the documents than real queries would, which favors lexical retrieval. The labels come from a single annotator and have not been independently reviewed. The samples are small (26 test questions, 37 test citations), so intervals are wide and several retriever comparisons are inside the noise. The live comparison depends on the model behind a changing `latest` alias and on sampling randomness, and its recall score uses a keyword rule that is a proxy for human judgment. Retrieval was evaluated on an index spanning all 12 documents, which is harder than the application's per-project index.

## Stack

Backend: FastAPI, SQLAlchemy, SQLite (the `DATABASE_URL` environment variable can be pointed at Postgres for a persistent deployment). Google Gemini via the `google-genai` SDK for structured LLM output. TF-IDF (scikit-learn) for retrieval. `python-docx` and `python-pptx` for generating the Word and PowerPoint deliverables, including a native PowerPoint table with cell-level color formatting for the heat map slide, built without an image or charting dependency.

Frontend: React, Vite, TypeScript, Tailwind CSS.

## Running it locally

Backend:

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# a free key is available at https://aistudio.google.com/apikey, no card required
uvicorn app.main:app --reload --port 8000
```

Frontend:

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

## Project layout

```
backend/app/
  ai/            Gemini client, prompts, RAG retrieval, structured-output schemas, citation verification
  db/models.py   SQLAlchemy data model, 17 tables
  services/      business logic, one module per domain: impact, raci, raid, comms, training, exports
  routers/       HTTP layer over services/
  exporters/     docx and pptx document builders
backend/eval/    labeled evaluation set, retrievers under test, metrics, and runners (see Evaluation)
frontend/src/
  pages/         one page per domain area
  components/    heatmap/, adkar/, approvals/, ui/
  api/           typed REST client
```

## Scope and limitations

Authentication is out of scope; this was built as a single-user tool. Schema management relies on SQLAlchemy's `create_all()` rather than a migration framework, which is adequate at this scale but not intended to scale further as-is. The application is deployed on a free-tier host without persistent disk storage, so the SQLite database resets on redeploy; this is the reason for the automatic seed step rather than a manual data-loading process. A production deployment would use Postgres and add authenticated reviewer accounts.

## Contact

From [Yashasvi Jaiswal](https://yashjswl.com).

LinkedIn: [linkedin.com/in/yashjswl](https://www.linkedin.com/in/yashjswl/)

Email: [hello@yashjswl.com](mailto:hello@yashjswl.com)

---

&copy; 2026 Yashasvi Jaiswal. All rights reserved.
