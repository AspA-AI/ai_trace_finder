# Investigation trajectory artifacts

Each completed investigation run writes a human-readable trajectory artifact:

```text
backend/artifacts/runs/<investigation_id>/<run_id>.json
backend/artifacts/runs/<investigation_id>/latest.json
```

The artifact is an audit record of the bounded agent workflow. It contains the
input clues, ordered decisions, provider outcomes, relevance gates, extraction
outcomes, errors, and final run summary. It does not contain API keys or hidden
provider credentials.

## Inspecting a run

1. Run the backend from `backend/` with `uvicorn app.main:app --reload`.
2. Start an investigation from the application or `POST /investigations`.
3. Open `/runs/<investigation_id>` for the readable timeline.
4. Open `GET /investigations/<investigation_id>/run` for the same structured
   artifact through the API.
5. For offline review, open `latest.json` in the investigation directory.

The `trajectory` array is ordered by `sequence`. Each event includes:

- `timestamp`: UTC event time
- `stage`: planning, orchestration, discovery, retrieval, or extraction
- `action`: the decision or operation recorded
- `status`: started, completed, or failed
- `details`: bounded, event-specific evidence for the decision

This is intentionally an observability artifact, not a private chain-of-
thought transcript. It records externally verifiable workflow actions and
outcomes, not hidden model reasoning.

## Evidence terminology

A **source node** means one retrieved source. A **verification relationship**
compares evidence from two source nodes. A **target connection** is the
strongest status of one source node relative to the investigation target. A
**verified source** participates in an accepted verification relationship,
while a **verified link** is the underlying accepted comparison that produced
that status. The graph shows target connections directly and exposes
source-to-source relationships as details.
