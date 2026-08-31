# TRACE submission checklist

This is the judge-facing handoff for the current build. It identifies what is
ready, where the evidence lives, and what must be shown or verified before
submission.

## Ready in the repository

- [x] Complete backend and frontend source code
- [x] Root ethical-use statement and intended-user definition: [README.md](README.md)
- [x] Root reproduction guide: [REPRODUCTION.md](REPRODUCTION.md)
- [x] Saved 15-case baseline/agent comparison:
      `backend/artifacts/evaluation/comparison.md`
- [x] Machine-readable evaluation evidence:
      `backend/artifacts/evaluation/comparison.json`
- [x] Representative agent trajectory manifest:
      `backend/artifacts/runs/manifest.json`
- [x] Human-readable trajectory inspection guide:
      `backend/artifacts/runs/README.md`
- [x] Changelog of measurable iterations:
      `backend/CHANGELOG.md`
- [x] Frontend production build validated with `npm run build`
- [x] Backend compilation and trajectory smoke test validated

## Demo path

1. Start the backend and frontend using `REPRODUCTION.md`.
2. Open the workspace and submit a public, permitted research target.
3. Show the result summary: source relevance, observations, and verification
   states.
4. Open the run trace and show the planned queries, search outcomes, relevance
   decisions, extraction gates, and final stop decision.
5. Open the evidence graph and click a source or verification relationship to
   inspect its URL and supporting details.
6. Open the evaluation page and show the baseline-versus-agent table.

## Evidence a reviewer should inspect

The most important claim is that TRACE is safer on identity collisions because
it can abstain when the evidence does not provide a sufficient identity anchor.
Review this together with the challenging Jordan Lee case in
`backend/artifacts/evaluation/comparison.json`; do not present abstention as
proof of correctness without the labeled ground truth.

The trajectory artifact demonstrates observable agent behavior rather than
hidden chain-of-thought. Reviewers can see the bounded plan, provider calls,
relevance gates, retries/errors, extraction decisions, and stop condition.

## Final checks before submission

- [ ] Run the evaluation from a clean environment and attach the regenerated
      JSON/Markdown reports.
- [x] Confirm at least ten labeled cases with public, permitted source URLs and
      reviewer-approved ground truth.
- [x] Confirm the benchmark has 15 labeled cases, exceeding the hackathon's
      stated ten-or-more target. A 20-case benchmark remains an optional
      project-specification expansion, not a hackathon requirement.
- [x] Run `pytest -q` after installing the optional test dependencies listed in
      `REPRODUCTION.md` — 28 tests passed.
- [ ] Replace any local absolute paths in reports intended for distribution
      with repository-relative paths.
- [ ] Confirm `.env`, API keys, personal data, and private source content are
      excluded from the submission.
- [ ] Record the final demo run ID and trajectory artifact in the submission
      notes.
- [ ] Explain that results support human review and are not an automated
      consequential decision.

## Evidence language

Use one vocabulary in the demo: a source node is one retrieved source; a
verification relationship compares two source nodes; a target connection is a
source node’s strongest status relative to the target; a verified source
participates in an accepted relationship; and a verified link is the
underlying accepted comparison.

## Current limitations to disclose

- Live discovery and baseline comparison require provider credentials and may
      incur usage charges.
- The offline verification evaluation uses saved evidence and is therefore
      reproducible without network access, but it is not a statistically
      calibrated estimate of production precision or recall.
- Public pages can be stale, blocked, duplicated, or incomplete; the system
      preserves those uncertainty states instead of treating absence of
      evidence as disproof.
