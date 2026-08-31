# Baseline vs TRACE Evaluation

The primary safety metric is false identity merge rate. Supporting metrics and individual hard cases follow.

```text
METRIC                       | SIMPLE BASELINE | TRACE          | CHANGE
False identity merge rate   |          35.71% |         0.00% | -35.71 pts
Correct identity resolution |          66.67% |       100.00% | +33.33 pts
Abstention rate             |          60.00% |        93.33% | +33.33 pts
```

## Individual hard cases

| Case | Expected | Simple baseline | TRACE | Baseline false merge | TRACE false merge |
|---|---|---|---|---:|---:|
| `common_name_identity_collision` | uncertain | uncertain | uncertain | no | no |
| `ambiguous_chris_lee_austin` | uncertain | uncertain | uncertain | no | no |
| `ambiguous_michael_smith_austin` | uncertain | uncertain | uncertain | no | no |
| `ambiguous_jordan_lee_seattle` | uncertain | resolved | uncertain | yes | no |
| `ambiguous_taylor_brown_austin` | uncertain | uncertain | uncertain | no | no |
| `ambiguous_david_kim_seattle` | uncertain | uncertain | uncertain | no | no |
| `ambiguous_jamie_chen_toronto` | uncertain | uncertain | uncertain | no | no |
| `ambiguous_alex_johnson_austin` | uncertain | uncertain | uncertain | no | no |
| `ambiguous_sam_lee_new_york` | uncertain | uncertain | uncertain | no | no |
| `ekram_yeshanew_software_developer` | uncertain | uncertain | uncertain | no | no |
| `olivia_dean_singer` | uncertain | resolved | uncertain | yes | no |
| `michael_tamire_salesman` | uncertain | resolved | uncertain | yes | no |
| `steve_jobs_developer` | uncertain | resolved | uncertain | yes | no |
| `katie_james_ai_consultant` | uncertain | resolved | uncertain | yes | no |

## Supporting metrics

Metrics requiring data not present in the saved benchmark are marked unavailable rather than estimated.

| Metric | Simple baseline | TRACE |
|---|---:|---:|
| `abstention_accuracy` | 64.29% | 100.00% |
| `contradiction_detection` | unavailable | 100.00% |
| `field_accuracy` | unavailable | unavailable |
| `latency` | unavailable | unavailable |
| `cost_per_investigation` | unavailable | unavailable |

The machine-readable report is in [comparison.json](comparison.json).
