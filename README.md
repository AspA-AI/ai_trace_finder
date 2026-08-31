# TRACE

TRACE is an evidence-first people-investigation workflow for authorized
researchers who need to organize public, permitted information and review how
identity conclusions were reached.

## Intended users

TRACE is designed for trained research analysts, investigative journalists,
trust-and-safety teams, and authorized compliance or due-diligence reviewers.
It is a decision-support tool: a human reviewer remains responsible for
checking sources, interpreting uncertainty, and deciding what action is
appropriate.

## Ethical use and boundaries

Use TRACE only for lawful, authorized research based on public or explicitly
permitted sources. Do not use it to stalk, harass, dox, monitor, or target
private individuals; infer sensitive traits; bypass access controls; or make
automated decisions about employment, housing, credit, insurance, education,
immigration, policing, or other high-impact eligibility.

TRACE does not establish identity from a name alone. It preserves source
provenance, exposes verification uncertainty, and is designed to abstain when
the evidence is insufficient or contradictory. Results must be independently
reviewed before any consequential use.

## Reproduce and review

- [Reproduction guide](REPRODUCTION.md) — install, configure, run, and inspect artifacts
- [Five-minute demo script](DEMO_SCRIPT.md) — judge-facing walkthrough
- [Submission checklist](SUBMISSION_CHECKLIST.md) — final handoff checks
- [Evaluation report](backend/artifacts/evaluation/comparison.md) — baseline comparison
- [Run-artifact guide](backend/artifacts/runs/README.md) — trajectory format and replay artifacts
- [Backend documentation](backend/README.md) — API and evidence-pipeline details

## Consistent evidence vocabulary

- **Source node:** one retrieved source.
- **Verification relationship:** a comparison between evidence from two sources.
- **Target connection:** a source’s projected status relative to the investigation.
- **Verified source:** a source participating in an accepted verification relationship.
- **Verified link:** the underlying comparison that produced that status.
## Database lifecycle

Run these commands from the repository root. They use the backend `.env` and
therefore operate on the same SQLite or Supabase PostgreSQL database as the
API:

```bash
make db-status    # show record counts
make db-migrate   # create missing tables/apply built-in migrations
make db-reset     # DELETE ALL application records, then recreate the schema
make db-seed FILE=path/to/cases.json
make artifacts-clean  # optional; deletes local JSON artifacts, not database data
```

`db-reset` is intentionally not reversible. It does not create sample
investigations because there is no canonical seed dataset in this project;
start new investigations through the UI/API. `db-seed` only inserts clue
records and does not perform retrieval, extraction, or verification.

Investigation API behavior is intentionally simple: `POST /investigations`
creates and runs a new case, while `PUT /investigations/{id}` replaces the
clues and reruns that existing case under the same ID. Verification is then
run through the existing `POST /investigations/{id}/verification` endpoint.
