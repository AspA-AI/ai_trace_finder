"""Intentionally simple one-call LLM baseline for apples-to-apples evaluation."""

import json
from datetime import datetime, timezone
from pathlib import Path

import httpx

from app.evidence_pipeline.evaluation.verification import BENCHMARK_PATH, REPORT_DIR
from app.evidence_pipeline.verification.artifacts import load_verification_artifact


def _parse_verdict(text: str) -> str:
    lower = text.lower()
    first_line = lower.splitlines()[0] if lower.splitlines() else lower
    if "same person" in first_line and "different" not in first_line:
        return "resolved"
    if "different/" in first_line or "unresolved" in first_line:
        return "uncertain"
    if "different" in first_line:
        return "unresolved"
    if "uncertain" in first_line:
        return "uncertain"
    if any(word in lower for word in ("different people", "not the same", "cannot confirm", "uncertain", "unclear", "not enough")):
        return "uncertain"
    if any(word in lower for word in ("same person", "is the same", "one person", "confidently same")):
        return "resolved"
    if any(word in lower for word in ("not the same person", "different person")):
        return "unresolved"
    return "uncertain"


def run_baseline_case(case: dict, api_key: str, model: str, timeout: float = 60.0) -> dict:
    artifact = load_verification_artifact(case["investigation_id"])
    if not artifact:
        return {"case_id": case["case_id"], "status": "missing_artifact", "verdict": "uncertain"}
    observations = artifact.get("stages", {}).get("observations", [])
    evidence = "\n".join(
        f"- {item.get('subject_text')}: {item.get('predicate')} = {item.get('object_text')} | {item.get('quote')} | {item.get('source_url')}"
        for item in observations
    )
    prompt = (
        "Based only on the observations below, judge whether they describe one person. "
        "Answer in plain text. Start with exactly one of: SAME PERSON, DIFFERENT/UNRESOLVED, or UNCERTAIN. "
        "Then briefly list what you are confident about and what is unclear. Do not use outside knowledge.\n\n"
        f"TARGET INPUT: {json.dumps(case.get('clues', {}), ensure_ascii=False)}\nOBSERVATIONS:\n{evidence}"
    )
    with httpx.Client(timeout=timeout) as client:
        response = client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"model": model, "temperature": 0, "messages": [
                {"role": "system", "content": "You are a naive identity judgment baseline."},
                {"role": "user", "content": prompt},
            ]},
        )
        response.raise_for_status()
    raw = response.json()["choices"][0]["message"]["content"]
    return {"case_id": case["case_id"], "investigation_id": case["investigation_id"],
            "status": "completed", "model": model, "verdict": _parse_verdict(raw), "raw_response": raw,
            "ground_truth": case.get("ground_truth", {})}


def run_baseline_evaluation(api_key: str, model: str, timeout: float = 60.0) -> dict:
    cases = json.loads(BENCHMARK_PATH.read_text(encoding="utf-8"))
    results = []
    for case in cases:
        try:
            results.append(run_baseline_case(case, api_key, model, timeout))
        except Exception as exc:
            results.append({"case_id": case["case_id"], "investigation_id": case["investigation_id"],
                            "status": "error", "verdict": "uncertain", "error": str(exc)})
    report = {"report_type": "baseline_evaluation", "generated_at": datetime.now(timezone.utc).isoformat(),
              "strategy": "one direct LLM call over all saved observations; no deterministic or structured verification",
              "cases": results}
    path = REPORT_DIR / "baseline.json"
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report["report_path"] = str(path)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report
