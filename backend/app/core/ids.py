import re
from datetime import datetime, timezone
from pathlib import Path

from fastapi import HTTPException

SAFE_INVESTIGATION_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


def require_investigation_id(value: str | None) -> str:
    if not value or not SAFE_INVESTIGATION_ID.fullmatch(value) or ".." in value:
        raise HTTPException(status_code=400, detail="Invalid investigation_id")
    return value


def artifact_dir(root: Path, investigation_id: str) -> Path:
    """Return a directory under root for this investigation; reject path escape."""
    investigation_id = require_investigation_id(investigation_id)
    resolved_root = root.resolve()
    path = (resolved_root / investigation_id).resolve()
    if path != resolved_root and resolved_root not in path.parents:
        raise HTTPException(status_code=400, detail="Invalid investigation_id")
    return path


def parse_utc(value: str) -> datetime:
    text = (value or "").replace("Z", "+00:00")
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)
