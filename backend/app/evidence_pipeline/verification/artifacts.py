import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from app.core.ids import artifact_dir


ARTIFACT_DIR = Path(__file__).resolve().parents[3] / "artifacts" / "verification"


def save_verification_artifact(
    investigation_id: str, stages: dict, run_id: str | None = None
) -> dict:
    """Persist one verification run without overwriting prior runs for the
    same investigation. Each run gets its own file under the
    investigation's folder; a `latest.json` pointer is also kept so callers
    that only care about the current result don't need to track run_ids."""
    investigation_dir = artifact_dir(ARTIFACT_DIR, investigation_id)
    investigation_dir.mkdir(parents=True, exist_ok=True)

    run_id = run_id or uuid.uuid4().hex[:12]
    generated_at = datetime.now(timezone.utc).isoformat()
    payload = {
        "investigation_id": investigation_id,
        "run_id": run_id,
        "generated_at": generated_at,
        "stages": stages,
    }
    serialized = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"

    run_path = investigation_dir / f"{run_id}.json"
    run_path.write_text(serialized, encoding="utf-8")

    latest_path = investigation_dir / "latest.json"
    latest_path.write_text(serialized, encoding="utf-8")

    return {"run_id": run_id, "path": str(run_path), "latest_path": str(latest_path)}


def list_verification_runs(investigation_id: str) -> list[str]:
    """Run_ids available for this investigation, most recent first."""
    investigation_dir = artifact_dir(ARTIFACT_DIR, investigation_id)
    if not investigation_dir.exists():
        return []
    run_ids = [p.stem for p in investigation_dir.glob("*.json") if p.stem != "latest"]
    return sorted(run_ids, reverse=True)


def load_verification_artifact(investigation_id: str, run_id: str | None = None) -> dict | None:
    """Load a specific run, or the latest one if run_id is omitted."""
    investigation_dir = artifact_dir(ARTIFACT_DIR, investigation_id)
    path = investigation_dir / (f"{run_id}.json" if run_id else "latest.json")
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))
