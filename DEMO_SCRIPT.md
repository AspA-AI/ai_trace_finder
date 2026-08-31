# TRACE five-minute demo script

This script keeps the demo focused on the project’s differentiator: evidence-
grounded identity research with visible decisions and safe uncertainty.

## Before recording

1. Follow [REPRODUCTION.md](REPRODUCTION.md) to start the backend and
   frontend.
2. Confirm the workspace opens at `http://localhost:3000`.
3. Keep one completed investigation ready so the demo does not depend on a
   live provider response at recording time.
4. Keep the saved comparison report and one trajectory artifact available.

## Suggested five-minute flow

### 0:00–0:35 — Problem and promise

“TRACE investigates a person from public, permitted clues. The important
output is not a name guess; it is a source-grounded result that shows what was
found, what was accepted, what was rejected, and where the system remains
uncertain.”

### 0:35–1:25 — Start an investigation

Open **New investigation**, enter a target and a small set of clues, and submit
it. Point out that the run returns an investigation ID and immediately opens
the run trace.

### 1:25–2:25 — Show agent behavior

On **How TRACE reached this result**, point to:

- the planned search formulations;
- the bounded discovery rounds and result counts;
- retrieval and relevance decisions, including filtered sources;
- extraction decisions and any provider errors;
- the final stop decision and run summary.

Open one event’s details to show that the decision is inspectable as structured
data. Explain that this is an audit trail of observable actions, not hidden
chain-of-thought.

### 2:25–3:25 — Show evidence and verification

Return to the investigation workspace. Open the evidence trail and select a
source to show its original URL, relevance score, explanation, and extracted
claims. Open the graph to show verified/probable/unknown states and click a
source or relationship to inspect its supporting details.

Emphasize that source lines and verification states are kept distinct: a
source can be relevant without being a verified identity link.

Use the terminology explicitly: a source node is one retrieved source; a
verification relationship compares evidence from two source nodes; a target
connection is the source node’s strongest status relative to the investigation;
a verified source participates in an accepted verification relationship; and a
verified link is the underlying accepted comparison. A relevant source is not
automatically a verified identity link.

### 3:25–4:20 — Show the safety behavior

Use the common-name collision result or the Jordan Lee benchmark case. Show
that conflicting or insufficient evidence remains uncertain instead of being
silently merged. State that the output supports human review and is not an
automated consequential decision.

### 4:20–5:00 — Show measured improvement and reproducibility

Open **Measured improvement** and show the saved baseline-versus-agent table.
Then briefly open `REPRODUCTION.md` and explain that a reviewer can run the
offline evaluation against saved evidence without Supabase or network access.

Close with: “Every claim is tied to evidence, every run has a trajectory, and
the system is designed to abstain when identity evidence is not strong enough.”

Terminology reminder: Source node; Verification relationship; Target connection; Verified source; Verified link.

## Backup commands

```bash
# Offline agent evaluation; no provider credentials required
curl -sS -X POST http://127.0.0.1:8000/evaluations/verification

# Baseline comparison; requires OPENAI_API_KEY
curl -sS -X POST http://127.0.0.1:8000/evaluations/comparison
```
