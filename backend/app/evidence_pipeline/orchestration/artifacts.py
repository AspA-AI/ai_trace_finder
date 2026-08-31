"""Persist replayable, human-readable investigation run trajectories."""

import json
from pathlib import Path

from app.core.ids import artifact_dir


ARTIFACT_DIR = Path(__file__).resolve().parents[3] / "artifacts" / "runs"


def save_run_artifact(investigation_id: str, run_id: str, payload: dict) -> dict:
    run_dir = artifact_dir(ARTIFACT_DIR, investigation_id)
    run_dir.mkdir(parents=True, exist_ok=True)
    path = run_dir / f"{run_id}.json"
    latest = run_dir / "latest.json"
    serialized = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    path.write_text(serialized, encoding="utf-8")
    latest.write_text(serialized, encoding="utf-8")
    return {"run_id": run_id, "path": str(path), "latest_path": str(latest)}


def load_latest_run_artifact(investigation_id: str) -> dict | None:
    path = artifact_dir(ARTIFACT_DIR, investigation_id) / "latest.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))
