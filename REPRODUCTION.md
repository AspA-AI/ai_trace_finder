# TRACE reproduction guide

Before running a live investigation, review the [ethical-use and intended-user
boundaries](README.md#ethical-use-and-boundaries). Use only public, permitted
research targets and keep a human reviewer in the loop.

This guide takes a reviewer from a clean checkout to a working investigation,
an offline agent evaluation, and a baseline comparison. Run commands from the
repository root unless the command changes directory explicitly.

## 1. Runtime and versions

- Python: 3.11 or newer (3.12 recommended; the backend declares `>=3.11`).
- Node.js: 20 LTS recommended (Next.js 15 requires Node.js 18.18 or newer).
- Backend: FastAPI `>=0.115,<1`, Pydantic `>=2.8,<3`, Uvicorn `>=0.30,<1`,
  psycopg `>=3.2,<4`, BeautifulSoup4 `>=4.12,<5`, and lxml `>=5,<6`.
- Frontend: Next.js `15.4.0`, React `19.0.0`, React DOM `19.0.0`.
- The exact frontend transitive versions are locked in
  `frontend/package-lock.json`. Backend dependencies are range-pinned in
  `backend/requirements.txt`; use a fresh virtual environment for a clean
  install.

Check local runtimes with:

```bash
python3 --version
node --version
npm --version
```

## 2. Install the backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate       # Windows: .venv\\Scripts\\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

For the automated test suite, install its explicitly optional tools:

```bash
python -m pip install "pytest>=8,<9" "pytest-asyncio>=0.23,<1"
```

## 3. Install the frontend

In a second terminal:

```bash
cd frontend
npm ci
```

## 4. Configure `.env`

Create the backend environment file:

```bash
cd backend
cp .env.example .env
```

Set these values as available:

```dotenv
TAVILY_API_KEY=your_tavily_key
OPENAI_API_KEY=your_openai_key
GITHUB_TOKEN=                 # optional, only needed for GitHub API access
DATABASE_URL=sqlite:///./people_investigation.db
```

Never commit `.env` or expose these values in screenshots, artifacts, or the
frontend. `OPENAI_API_KEY` is needed for observation extraction, re-extraction,
and the direct baseline comparison. `TAVILY_API_KEY` is needed for live web
discovery.

## 5. Database setup

Supabase is optional. The default SQLite configuration is sufficient for a
local demonstration and creates `backend/people_investigation.db` on demand.

To use Supabase or another PostgreSQL service, set `DATABASE_URL` to its
PostgreSQL connection string. The application creates its tables on startup.
Use a connection string accepted by psycopg; do not append the Supabase-only
`pgbouncer=true` query parameter. TRACE already removes that parameter, but
omitting it avoids ambiguity. pgvector is not required by the current
evidence, verification, or evaluation workflows.

## 6. Start the services

Backend terminal:

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

Frontend terminal:

```bash
cd frontend
npm run dev -- -p 3000
```

Open <http://localhost:3000>. The frontend proxies `/api/*` requests to
`http://127.0.0.1:8000` by default. To use another backend URL:

```bash
BACKEND_URL=http://127.0.0.1:8000 npm run dev -- -p 3000
```

## 7. Run one live investigation

With both services running:

```bash
curl -sS -X POST http://127.0.0.1:8000/investigations \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Simon Willison",
    "occupation": "writer and software developer",
    "locations": [],
    "usernames": [],
    "employers": [],
    "websites": [],
    "github_handle": null,
    "additional_clues": []
  }'
```

The response includes an `investigation_id`, `run_id`, `trajectory`, and
`trajectory_artifact`. Open `/runs/<investigation_id>` to inspect the same
decision timeline in the UI. The raw JSON is saved under
`backend/artifacts/runs/<investigation_id>/latest.json`.

## 8. Run the saved-evidence agent evaluation (offline)

This does not perform web discovery or call an LLM. It evaluates the saved
verification artifacts listed in
`backend/datasets/verification_benchmark.json` (currently 15 labeled cases):

```bash
curl -sS -X POST http://127.0.0.1:8000/evaluations/verification
```

Or directly from the backend environment:

```bash
cd backend
source .venv/bin/activate
python -c "from app.evidence_pipeline.evaluation.verification import run_verification_evaluation; print(run_verification_evaluation()['summary'])"
```

Review the result at `backend/artifacts/evaluation/latest.json`.

## 9. Run the simple baseline and comparison

The baseline is intentionally one direct OpenAI call over the same saved
observations for each benchmark case. It has no deterministic verification,
candidate generation, authority weighting, or confidence formula. The
comparison endpoint runs both the baseline and the saved-evidence agent
evaluation, then writes both reports:

```bash
curl -sS -X POST http://127.0.0.1:8000/evaluations/comparison
```

This step requires `OPENAI_API_KEY` and internet access to the OpenAI API. The
outputs are:

- `backend/artifacts/evaluation/baseline.json`
- `backend/artifacts/evaluation/comparison.json`
- `backend/artifacts/evaluation/comparison.md`

The UI view is <http://localhost:3000/evaluation>.

To rebuild the comparison report entirely from the already saved baseline and
verification artifacts, without calling OpenAI:

```bash
cd backend
source .venv/bin/activate
python -c "from app.evidence_pipeline.evaluation.comparison import run_saved_comparison_evaluation; print(run_saved_comparison_evaluation()['comparison_table'])"
```

This saved comparison is the zero-cost, offline path for reviewing the
headline false-merge result and individual hard cases.

## 10. Run automated checks

```bash
cd backend
source .venv/bin/activate
pytest -q
```

The frontend production check is:

```bash
cd frontend
npm run build
```

## 11. Inspecting outputs

- Raw sources and observations: `backend/artifacts/` and the configured
  database.
- Verification runs: `backend/artifacts/verification/<investigation_id>/`.
- Agent run trajectories: `backend/artifacts/runs/<investigation_id>/`.
- Trajectory format and representative artifact:
  `backend/artifacts/runs/README.md` and `manifest.json`.
- Baseline/agent metrics: `backend/artifacts/evaluation/comparison.md` and
  `comparison.json`.

The run page shows observable workflow actions and outcomes. It does not claim
to expose hidden model chain-of-thought; the artifact is designed for audit,
replay, and reviewer inspection.

## 12. Expected output, runtime, and API cost

A successful live run returns a shape like:

```json
{
  "investigation_id": "inv_<12 hex characters>",
  "run_id": "run_<12 hex characters>",
  "status": "completed",
  "query_count": 3,
  "retrieved_source_count": 5,
  "observation_count": 12,
  "trajectory_artifact": {
    "path": "backend/artifacts/runs/<investigation_id>/<run_id>.json"
  }
}
```

Runtime depends on provider latency and source count. A small live run is
normally measured in seconds to a few minutes; the saved-evidence evaluation
is normally seconds. Cost is provider-dependent rather than fixed in this
repository: one live run may use several Tavily queries, optional GitHub/web
retrieval, and one extraction call per relevant source. The 15-case baseline
comparison uses one OpenAI call per case, plus any extraction calls already
represented by the saved evidence. As a planning estimate, a small 15-case
run is usually cents to low single-digit USD, but reviewers should confirm
current provider pricing and their own token/source counts before running it.

For a zero-cost review, use the saved-evidence verification evaluation and
inspect the committed JSON artifacts; no Supabase, Tavily, GitHub, or OpenAI
credential is required for that offline path.

## Evidence terminology

A **source node** is one retrieved source. A **verification relationship** is a
comparison between evidence from two source nodes. A **target connection** is
the source node’s strongest status relative to the investigation target. A
**verified source** participates in an accepted verification relationship. A
**verified link** is the underlying accepted comparison that produced that
status.
