# AI Change Impact Studio

Most "AI wrapper" side projects are a chat window bolted onto a prompt. I wanted to see whether an LLM pipeline could hold up against a real methodology instead of just sounding plausible, so this is built around how change management is actually run at a firm like PwC, not around what looks good in a demo.

You describe a business change, moving from manual to automated onboarding, migrating a billing system, whatever it is, and the app produces a stakeholder impact assessment scored against Prosci's ADKAR model, a Red/Amber/Green readiness heat map, a RACI matrix, a RAID log, a communications plan, a training needs matrix, and exportable Word/PowerPoint deliverables you could actually hand to a steering committee.

It started as a single Streamlit script (still sitting in `../ai-change-impact-assistant/` if you want the before/after). I rebuilt it into a proper FastAPI + React app once it became clear the impact analysis needed to be more than a JSON blob with a UI on top: a real data model, editable stakeholder scores, an approval trail, things that make it usable by more than one person in one sitting.

## How the scoring actually works

The interesting part isn't the LLM call, it's turning five ADKAR scores per stakeholder into something you can act on. Prosci's framework says readiness isn't an average of Awareness, Desire, Knowledge, Ability, and Reinforcement, it's gated by whichever of those five is weakest first. A stakeholder scoring 5/5/2/5/5 isn't "80% ready," they're stuck on Knowledge, and everything downstream of that is noise until it's fixed. So `impact_service.py` finds the first dimension scoring 3 or below and weights the readiness score 65/35 toward that barrier over the raw average. That score, plus an LLM-assigned impact severity, gets banded into a 3x3 grid and mapped to Red/Amber/Green through an explicit lookup table, unit tested against all nine cells rather than trusted to "look about right."

Citations from the document comparison tool get the same treatment. Instead of trusting the model's claim that an excerpt came from a given source, `citation_verify.py` checks the excerpt against the actual retrieved chunk before the UI is allowed to label it "Verified."

## Stack

FastAPI, SQLAlchemy, SQLite (swap `DATABASE_URL` for Postgres if you need it to survive a redeploy). Google Gemini for structured output. TF-IDF for retrieval instead of an embedding model, four sample documents don't need a vector database. React, Vite, TypeScript, and Tailwind on the frontend. `python-docx` and `python-pptx` for the exports, which turned out to be the part I underestimated, getting a native PowerPoint table to color its own cells red, amber, and green without shipping a matplotlib image took longer than the ADKAR math did.

## Running it locally

Backend:

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# grab a free key at https://aistudio.google.com/apikey, no card needed
uvicorn app.main:app --reload --port 8000
```

Frontend:

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

The first time the backend boots against an empty database it seeds a sample initiative on its own, an onboarding-automation scenario with documents already attached, so there's something to click into instead of a blank screen. It won't touch a database that already has data in it.

## Layout

```
backend/app/
  ai/            Gemini wrapper, prompts, RAG, structured-output schemas, citation verification
  db/models.py   the data model, 17 tables
  services/      business logic, one file per domain: impact, raci, raid, comms, training, exports...
  routers/       thin HTTP layer over services/
  exporters/     docx/pptx builders
frontend/src/
  pages/         one per domain area
  components/    heatmap/, adkar/, approvals/, ui/
  api/           typed REST client
```

## What's not here

No auth, this was scoped as a single-user tool. No real migration tooling, `create_all()` is the whole schema story, which is fine at this size and won't stay fine forever. It's deployed for free, so the SQLite file resets on every Render redeploy since the free tier has no persistent disk, hence the auto-seed step instead of a manual data-loading story. If I picked this back up, Postgres and a proper reviewer login would be first on the list.

Deployment notes are in [DEPLOYMENT.md](DEPLOYMENT.md).
