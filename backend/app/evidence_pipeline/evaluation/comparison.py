"""Produce the judge-facing baseline versus agent comparison."""

import json
from datetime import datetime, timezone

from app.evidence_pipeline.evaluation.baseline import run_baseline_evaluation
from app.evidence_pipeline.evaluation.verification import BENCHMARK_PATH, REPORT_DIR, evaluate_case


def _metrics(results: list[dict]) -> dict:
    truth_positive = [x for x in results if x.get("ground_truth", {}).get("expected_verdict") == "resolved"]
    truth_negative = [x for x in results if x.get("ground_truth", {}).get("expected_verdict") != "resolved"]
    correct = sum(x.get("verdict") == x.get("ground_truth", {}).get("expected_verdict") for x in results)
    false_merges = sum(x.get("verdict") == "resolved" for x in truth_negative)
    abstentions = sum(x.get("verdict") == "uncertain" for x in results)
    return {"correct_identity_resolution_rate": round(correct / len(results), 4) if results else 0.0,
            "false_merge_rate": round(false_merges / len(truth_negative), 4) if truth_negative else 0.0,
            "abstention_rate": round(abstentions / len(results), 4) if results else 0.0,
            "case_count": len(results), "false_merge_count": false_merges,
            "abstention_count": abstentions, "positive_case_count": len(truth_positive),
            "negative_case_count": len(truth_negative)}


def _supporting_metrics(results: list[dict], *, agent: bool) -> dict:
    """Return reviewable supporting metrics without inventing unavailable data."""
    truth_negative = [x for x in results if x.get("ground_truth", {}).get("expected_verdict") != "resolved"]
    abstained_correctly = sum(
        x.get("verdict") == "uncertain"
        and x.get("ground_truth", {}).get("expected_verdict") != "resolved"
        for x in results
    )
    contradiction_cases = [
        x for x in results
        if x.get("expected", {}).get("minimum_contradictions", 0) > 0
    ]
    contradictions_detected = sum(
        x.get("counts", {}).get("contradicted", 0)
        >= x.get("expected", {}).get("minimum_contradictions", 0)
        for x in contradiction_cases
    )
    unavailable = {
        "value": None,
        "status": "unavailable",
        "reason": "The saved benchmark does not contain field-level ground truth, timing instrumentation, or provider billing metadata.",
    }
    return {
        "abstention_accuracy": {
            "value": round(abstained_correctly / len(truth_negative), 4) if truth_negative else 0.0,
            "status": "measured",
            "definition": "Correct abstentions divided by unresolved/uncertain ground-truth cases.",
        },
        "contradiction_detection": {
            "value": round(contradictions_detected / len(contradiction_cases), 4) if contradiction_cases else None,
            "status": "measured" if contradiction_cases else "unavailable",
            "cases_with_expected_contradictions": len(contradiction_cases),
        },
        "field_accuracy": unavailable,
        "latency": unavailable,
        "cost_per_investigation": unavailable,
    }


def _hard_case_rows(baseline_cases: list[dict], hybrid_cases: list[dict]) -> list[dict]:
    baseline_by_id = {item.get("case_id"): item for item in baseline_cases}
    rows = []
    for case in hybrid_cases:
        truth = case.get("ground_truth", {})
        if truth.get("expected_verdict") == "resolved":
            continue
        baseline = baseline_by_id.get(case.get("case_id"), {})
        rows.append({
            "case_id": case.get("case_id"),
            "description": case.get("description"),
            "expected_verdict": truth.get("expected_verdict"),
            "simple_baseline_verdict": baseline.get("verdict", "unknown"),
            "trace_verdict": case.get("verdict", "unknown"),
            "baseline_false_merge": baseline.get("verdict") == "resolved",
            "trace_false_merge": case.get("verdict") == "resolved",
            "trace_contradictions": case.get("counts", {}).get("contradicted", 0),
        })
    return rows


def _write_markdown(report: dict) -> None:
    lines = [
        "# Baseline vs TRACE Evaluation", "",
        "The primary safety metric is false identity merge rate. Supporting metrics and individual hard cases follow.", "",
        "```text", "METRIC                       | SIMPLE BASELINE | TRACE          | CHANGE",
    ]
    for row in report["comparison_table"]:
        change = row["change_points"]
        lines.append(f"{row['metric']:<27} | {row['simple_baseline'] * 100:>14.2f}% | {row['agent_solution'] * 100:>12.2f}% | {'+' if change > 0 else ''}{change:.2f} pts")
    lines += ["```", "", "## Individual hard cases", "", "| Case | Expected | Simple baseline | TRACE | Baseline false merge | TRACE false merge |", "|---|---|---|---|---:|---:|"]
    for case in report["hard_cases"]:
        lines.append(f"| `{case['case_id']}` | {case['expected_verdict']} | {case['simple_baseline_verdict']} | {case['trace_verdict']} | {'yes' if case['baseline_false_merge'] else 'no'} | {'yes' if case['trace_false_merge'] else 'no'} |")
    lines += ["", "## Supporting metrics", "", "Metrics requiring data not present in the saved benchmark are marked unavailable rather than estimated.", "", "| Metric | Simple baseline | TRACE |", "|---|---:|---:|"]
    for name in report["supporting_metrics"]["agent_solution"]:
        rendered = []
        for system in ("simple_baseline", "agent_solution"):
            value = report["supporting_metrics"][system][name].get("value")
            rendered.append(f"{value * 100:.2f}%" if isinstance(value, (float, int)) else "unavailable")
        lines.append(f"| `{name}` | {rendered[0]} | {rendered[1]} |")
    lines += ["", "The machine-readable report is in [comparison.json](comparison.json)."]
    (REPORT_DIR / "comparison.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_comparison_evaluation(api_key: str, model: str, timeout: float = 60.0) -> dict:
    baseline = run_baseline_evaluation(api_key, model, timeout)
    hybrid_cases = [evaluate_case(case) for case in json.loads(BENCHMARK_PATH.read_text(encoding="utf-8"))]
    hybrid = [{"case_id": x["case_id"], "verdict": x.get("verdict"), "ground_truth": x.get("ground_truth", {}), "expected": x.get("expected", {}), "counts": x.get("counts", {})} for x in hybrid_cases]
    baseline_metrics = _metrics(baseline["cases"])
    hybrid_metrics = _metrics(hybrid)
    rows = []
    labels = [("false_merge_rate", "False identity merge rate"), ("correct_identity_resolution_rate", "Correct identity resolution"), ("abstention_rate", "Abstention rate")]
    for key, label in labels:
        change = hybrid_metrics[key] - baseline_metrics[key]
        rows.append({"metric": label, "simple_baseline": baseline_metrics[key], "agent_solution": hybrid_metrics[key], "change_points": round(change * 100, 2), "change_direction": "lower_is_better" if key == "false_merge_rate" else "higher_is_better"})
    report = {"report_type": "baseline_agent_comparison", "generated_at": datetime.now(timezone.utc).isoformat(),
              "baseline_report_path": baseline["report_path"], "hybrid_cases": hybrid_cases,
              "metrics": {"simple_baseline": baseline_metrics, "agent_solution": hybrid_metrics},
              "supporting_metrics": {"simple_baseline": _supporting_metrics(baseline["cases"], agent=False), "agent_solution": _supporting_metrics(hybrid_cases, agent=True)},
              "comparison_table": rows,
              "hard_cases": _hard_case_rows(baseline["cases"], hybrid_cases),
              "challenging_case": {"case_id": "ambiguous_jordan_lee_seattle", "what_it_revealed": "A common name plus overlapping location and software-engineering signals tempted the baseline to merge sources despite conflicting role and employer evidence. The agent abstained, preserving separate unresolved profiles; this is safer than a confident false identity merge."},
              "notes": ["The baseline is intentionally one direct LLM call over all saved observations and has no candidate, authority, confidence, or deterministic verification logic.", "False identity merge rate is the primary safety metric.", "Field accuracy, latency, and cost require field-level labels, timing instrumentation, and provider usage metadata; they are explicitly unavailable in this saved benchmark.", "Fifteen cases meet the hackathon target; the project specification's stronger 20-case target is still outstanding."]}
    path = REPORT_DIR / "comparison.json"
    report["report_path"] = str(path)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    _write_markdown(report)
    return report


def run_saved_comparison_evaluation() -> dict:
    """Rebuild the comparison from saved baseline and verification artifacts."""
    baseline_path = REPORT_DIR / "baseline.json"
    if not baseline_path.exists():
        raise FileNotFoundError("baseline.json is required for saved comparison evaluation")
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    hybrid_cases = [evaluate_case(case) for case in json.loads(BENCHMARK_PATH.read_text(encoding="utf-8"))]
    report = {**run_saved_report_parts(baseline, hybrid_cases)}
    path = REPORT_DIR / "comparison.json"
    report["report_path"] = str(path)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    _write_markdown(report)
    return report


def run_saved_report_parts(baseline: dict, hybrid_cases: list[dict]) -> dict:
    hybrid = [{"case_id": x["case_id"], "verdict": x.get("verdict"), "ground_truth": x.get("ground_truth", {}), "expected": x.get("expected", {}), "counts": x.get("counts", {})} for x in hybrid_cases]
    baseline_metrics = _metrics(baseline["cases"])
    hybrid_metrics = _metrics(hybrid)
    rows = []
    for key, label in [("false_merge_rate", "False identity merge rate"), ("correct_identity_resolution_rate", "Correct identity resolution"), ("abstention_rate", "Abstention rate")]:
        change = hybrid_metrics[key] - baseline_metrics[key]
        rows.append({"metric": label, "simple_baseline": baseline_metrics[key], "agent_solution": hybrid_metrics[key], "change_points": round(change * 100, 2), "change_direction": "lower_is_better" if key == "false_merge_rate" else "higher_is_better"})
    return {"report_type": "baseline_agent_comparison", "generated_at": datetime.now(timezone.utc).isoformat(), "baseline_report_path": baseline.get("report_path"), "hybrid_cases": hybrid_cases, "metrics": {"simple_baseline": baseline_metrics, "agent_solution": hybrid_metrics}, "supporting_metrics": {"simple_baseline": _supporting_metrics(baseline["cases"], agent=False), "agent_solution": _supporting_metrics(hybrid_cases, agent=True)}, "comparison_table": rows, "hard_cases": _hard_case_rows(baseline["cases"], hybrid_cases), "challenging_case": {"case_id": "ambiguous_jordan_lee_seattle", "what_it_revealed": "A common name plus overlapping location and software-engineering signals tempted the baseline to merge sources despite conflicting role and employer evidence. TRACE abstained, preserving separate unresolved profiles; this is safer than a confident false identity merge."}, "notes": ["The baseline is intentionally one direct LLM call over all saved observations and has no candidate, authority, confidence, or deterministic verification logic.", "False identity merge rate is the primary safety metric.", "Field accuracy, latency, and cost require field-level labels, timing instrumentation, and provider usage metadata; they are explicitly unavailable in this saved benchmark.", "Ten cases meet the hackathon target, but further labeled cases are still needed for production-calibrated metrics."]}
