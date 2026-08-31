# People Investigation Backend

## Intended use and ethical boundaries

This backend supports authorized research analysts, investigative journalists,
trust-and-safety teams, and compliance or due-diligence reviewers working with
public, permitted sources. It is decision support, not an identity oracle.

Do not use it to stalk, harass, dox, monitor, or target private individuals;
infer sensitive traits; bypass access controls; or make automated decisions in
employment, housing, credit, insurance, education, immigration, policing, or
other high-impact contexts. A human reviewer must validate sources and decide
what action, if any, is appropriate. The system is designed to preserve
uncertainty and abstain when evidence is insufficient or contradictory.

The backend is organized by product capability. The current implementation
target is `evidence_pipeline`: discover public sources, retrieve them through
provider adapters, preserve raw evidence, and prepare source-grounded
observations for extraction.

## Where to look

- `app/api/` — FastAPI route definitions. This is the HTTP entry point only.
- `app/core/` — application settings and cross-cutting configuration.
- `app/evidence_pipeline/` — the single canonical pipeline implementation:
  discovery, retrieval, evidence persistence, extraction contracts, and
  orchestration.
- `tests/` — automated tests for the backend behavior.

The current delivery scope is retrieval and evidence ingestion, but the code is
named after the product capability rather than an implementation phase. Future
features should consume the evidence contracts instead of reaching directly
into provider implementations.

## Local setup

Copy `.env.example` to `.env` and add credentials when available. Secrets must
remain server-side and must not be committed.

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Use `?force_refresh=true` on `POST /investigations` when fresh retrieval is
needed. Otherwise, sources within the cache window are reused.

## Operational logging

The backend emits colorized, timestamped logs for HTTP requests and the major
pipeline stages: planning, discovery/retries, retrieval/cache decisions,
extraction, persistence, deterministic verification, and semantic review.
Each investigation log includes its investigation and run IDs plus elapsed
time. Set `LOG_LEVEL=DEBUG`, `INFO`, `WARNING`, or `ERROR` in `backend/.env` to
control verbosity. Secrets, prompts, and full source contents are never logged.

Phase 1 benchmark cases live in `datasets/phase1_benchmark.json`. Evaluation
helpers report retrieval success rate, latency, observations, and errors; they
do not make identity decisions.

The requirements file is used for local installation because this workspace
path contains braces (`A{sp}A`), which can confuse setuptools during editable
package installation. Run commands from `backend/` so the application package
is available on Python's import path.

The provider implementations are intentionally introduced behind interfaces so
the pipeline can be tested with fakes before external keys are configured.

## Evidence terminology

- **Source node** — one retrieved public source.
- **Verification relationship** — a comparison between evidence from two
  source nodes.
- **Target connection** — the strongest status assigned to a source node
  relative to the investigation target.
- **Verified source** — a source node participating in an accepted
  verification relationship.
- **Verified link** — the underlying comparison that produced an accepted
  status; it is not the source node itself.

The graph projects target connections as direct target-to-source spokes. The
underlying source-to-source verification relationships remain inspectable in
the relationship details.
