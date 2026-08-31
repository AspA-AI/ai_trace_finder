# Changelog

## Unreleased

- Added versioned, timestamped investigation trajectory artifacts and a reviewer-facing `/runs/<investigation_id>` timeline. Added the root-level reproduction guide covering live runs, saved-evidence evaluation, baseline comparison, runtime versions, database options, and cost expectations.
- Reworked the evaluation story so false identity merge rate is the headline metric, added abstention accuracy and contradiction detection, listed every hard case individually, and marked field accuracy, latency, and cost as unavailable until the benchmark records the required labels and instrumentation.
- Added a deliberately simple one-call LLM baseline and a saved comparison report. On the current two-case benchmark, both the baseline and agent solution resolve 100% of cases, false-merge rate is 0%, and abstention rate is 50%. This is directional evidence only until the benchmark reaches ten or more labeled cases.
- Expanded the benchmark to fifteen real saved investigations. On the current 15-case comparison, the baseline falsely merged five uncertain cases (35.71% false-merge rate) while TRACE maintained 0% false merges and 100% correct resolution; TRACE abstention increased to 93.33%. The project specification's stronger 20-case target remains outstanding.
