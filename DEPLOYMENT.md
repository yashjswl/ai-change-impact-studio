# Deployment: Frontend on Vercel, Backend on Render

## Order of operations

The two services need each other's URL (frontend needs the backend's URL to
call it; backend's CORS needs the frontend's URL to allow it), so deploy in
this order:

1. **Push to GitHub** (see below).
2. **Deploy the backend to Render** → note its URL (e.g. `https://ai-change-impact-studio-api.onrender.com`).
3. **Deploy the frontend to Vercel**, setting `VITE_API_URL` to that Render URL → note the Vercel URL (e.g. `https://your-app.vercel.app`).
4. **Go back to Render** and set `CORS_ORIGINS` to that Vercel URL, then redeploy the backend.

## 1. Push to GitHub

```bash
cd ai-change-impact-studio
git init
git add -A
git commit -m "Initial commit"
```

Create an empty repo on GitHub (via [github.com/new](https://github.com/new), or `gh repo create` if you have the CLI), then:

```bash
git remote add origin https://github.com/<you>/<repo>.git
git branch -M main
git push -u origin main
```

## 2. Backend on Render

[render.com](https://render.com) → **New +** → **Web Service** → connect your
GitHub repo. A `backend/render.yaml` blueprint is included, or configure
manually:

| Setting | Value |
|---|---|
| Root Directory | `backend` |
| Runtime | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |

Environment variables (Render dashboard → Environment):

| Key | Value |
|---|---|
| `GEMINI_API_KEY` | your key from [aistudio.google.com/apikey](https://aistudio.google.com/apikey) |
| `GEMINI_MODEL` | `gemini-flash-lite-latest` |
| `CORS_ORIGINS` | leave blank for now, set after step 3 |

Deploy, then copy the service URL Render gives you (something like
`https://ai-change-impact-studio-api.onrender.com`).

**Known limitation**: Render's free tier has no persistent disk, so the
SQLite database resets on every redeploy or restart (and the free tier also
spins down after inactivity, causing a ~30-60s cold start on the next
request). Fine for a portfolio demo; for anything longer-lived, upgrade to a
paid Render instance with a persistent disk, or switch `DATABASE_URL` to a
hosted Postgres (e.g. [Neon](https://neon.tech)'s free tier) — the app
already reads `DATABASE_URL` from the environment, so no code change is
needed, just set that env var to a Postgres connection string and add
`psycopg2-binary` to `requirements.txt`.

## 3. Frontend on Vercel

[vercel.com](https://vercel.com) → **Add New** → **Project** → import the
same GitHub repo.

| Setting | Value |
|---|---|
| Root Directory | `frontend` |
| Framework Preset | Vite (auto-detected) |
| Build Command | `npm run build` (default) |
| Output Directory | `dist` (default) |

Environment variable:

| Key | Value |
|---|---|
| `VITE_API_URL` | the Render backend URL from step 2, no trailing slash |

Deploy. Vercel gives you a URL like `https://your-app.vercel.app`.

## 4. Close the loop

Back in Render → Environment → set `CORS_ORIGINS` to your Vercel URL (comma-separate
multiple origins if needed, e.g. also `http://localhost:5173` for local dev), then
manually redeploy the backend so the new CORS setting takes effect.

## Verifying

Open the Vercel URL, create an initiative, click **Load Sample Docs**, and
run the impact analysis. If it hangs or errors, check the browser console
for a CORS or network error first — that almost always means step 4 (CORS)
or the `VITE_API_URL` value needs a fix.
