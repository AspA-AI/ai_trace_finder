"""Offline evaluation of saved verification runs against labeled benchmark cases."""

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from app.evidence_pipeline.contracts.evidence import Observation
from app.evidence_pipeline.reporting.synthesis import synthesize_profile
from app.evidence_pipeline.verification.artifacts import load_verification_artifact


BACKEND_DIR = Path(__file__).resolve().parents[3]
BENCHMARK_PATH = BACKEND_DIR / "datasets" / "verification_benchmark.json"
REPORT_DIR = BACKEND_DIR / "artifacts" / "evaluation"


def _check(name: str, actual, expected, passed: bool) -> dict:
    return {"name": name, "actual": actual, "expected": expected, "passed": passed}


def _hybrid_verdict(profile_status: str) -> str:
    return "resolved" if profile_status == "resolved" else "uncertain"


def evaluate_case(case: dict) -> dict:
    investigation_id = case["investigation_id"]
    artifact = load_verification_artifact(investigation_id)
    if not artifact:
        return {"case_id": case["case_id"], "investigation_id": investigation_id,
                "status": "missing_artifact", "passed": False, "checks": []}

    stages = artifact.get("stages", {})
    results = stages.get("final_results", [])
    observations = [Observation.model_validate(item) for item in stages.get("observations", [])]
    profile = synthesize_profile(investigation_id, observations, {"results": results})
    states = Counter(item.get("state") for item in results)
    identity = [item for item in results if item.get("comparison_type") == "identity_link"]
    positive = [item for item in identity if item.get("state") in {"VERIFIED", "PROBABLE"}]
    expected = case.get("expected", {})
    checks = [
        _check("minimum_candidates", len(stages.get("candidates", [])), expected.get("minimum_candidates", 0),
               len(stages.get("candidates", [])) >= expected.get("minimum_candidates", 0)),
        _check("minimum_verified", states["VERIFIED"], expected.get("minimum_verified", 0),
               states["VERIFIED"] >= expected.get("minimum_verified", 0)),
        _check("maximum_probable", states["PROBABLE"], expected.get("maximum_probable"),
               expected.get("maximum_probable") is None or states["PROBABLE"] <= expected["maximum_probable"]),
        _check("maximum_positive_links", len(positive), expected.get("maximum_positive_links"),
               expected.get("maximum_positive_links") is None or len(positive) <= expected["maximum_positive_links"]),
        _check("minimum_contradictions", states["CONTRADICTED"], expected.get("minimum_contradictions", 0),
               states["CONTRADICTED"] >= expected.get("minimum_contradictions", 0)),
        _check("profile_status", profile["status"], expected.get("profile_statuses", ["resolved", "ambiguous", "unresolved"]),
               profile["status"] in expected.get("profile_statuses", ["resolved", "ambiguous", "unresolved"])),
    ]
    return {
        "case_id": case["case_id"], "description": case.get("description"),
        "expected_behavior": case.get("expected_behavior", []), "reviewer_rationale": case.get("reviewer_rationale"),
        "investigation_id": investigation_id, "verification_run_id": artifact.get("run_id"),
        "artifact_generated_at": artifact.get("generated_at"), "status": "passed" if all(x["passed"] for x in checks) else "failed",
        "passed": all(x["passed"] for x in checks), "checks": checks,
        "counts": {"observations": len(observations), "candidates": len(stages.get("candidates", [])),
                   "comparisons": len(results), "identity_links": len(identity), "positive_identity_links": len(positive),
                   "verified": states["VERIFIED"], "probable": states["PROBABLE"], "unknown": states["UNKNOWN"],
                   "contradicted": states["CONTRADICTED"], "rejected": states["REJECTED"]},
        "profile": {"status": profile["status"], "source_count": profile["source_count"],
                    "candidate_profile_count": len(profile["candidate_profiles"])},
        "ground_truth": case.get("ground_truth", {}),
        "expected": expected,
        "verdict": _hybrid_verdict(profile["status"]),
    }


def run_verification_evaluation() -> dict:
    cases = json.loads(BENCHMARK_PATH.read_text(encoding="utf-8"))
    evaluated = [evaluate_case(case) for case in cases]
    totals = Counter()
    for item in evaluated:
        totals.update(item.get("counts", {}))
    total_comparisons = totals["comparisons"]
    report = {
        "report_type": "verification_evaluation",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "benchmark_path": str(BENCHMARK_PATH), "cases": evaluated,
        "summary": {
            "case_count": len(evaluated), "passed_cases": sum(x["passed"] for x in evaluated),
            "failed_cases": sum(not x["passed"] for x in evaluated), "totals": dict(totals),
            "abstention_rate": round(totals["unknown"] / total_comparisons, 4) if total_comparisons else 0.0,
            "positive_link_rate": round(totals["positive_identity_links"] / totals["identity_links"], 4) if totals["identity_links"] else 0.0,
        },
        "metric_notes": [
            "This is an acceptance evaluation of saved labeled cases, not a statistically calibrated precision/recall estimate.",
            "UNKNOWN is counted as abstention; it is preferable to an unsupported identity merge.",
            "The comparison table uses the same case-level verdict labels for both systems; false merges are positive verdicts on unresolved cases.",
        ],
    }
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORT_DIR / "latest.json"
    report["report_path"] = str(path)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report
