import re
import unicodedata
from datetime import datetime
from urllib.parse import urlsplit


LOCATION_ALIASES = {
    "sf": "san francisco",
    "s.f.": "san francisco",
    "wien": "vienna",
}


def normalize_text(value: str | None) -> str | None:
    if value is None:
        return None
    value = unicodedata.normalize("NFKC", value)
    value = " ".join(value.split()).strip().lower()
    return value or None


def normalize_name(value: str | None) -> str | None:
    value = normalize_text(value)
    if not value:
        return None
    value = "".join(
        char for char in unicodedata.normalize("NFKD", value)
        if not unicodedata.combining(char)
    )
    return re.sub(r"[^a-z0-9 ]", "", value).strip() or None


def normalize_username(value: str | None) -> str | None:
    value = normalize_text(value)
    if not value:
        return None
    return value.lstrip("@").replace(" ", "-")


def normalize_url(value: str | None) -> str | None:
    if not value:
        return None
    parts = urlsplit(value.strip())
    if not parts.scheme or not parts.netloc:
        return normalize_text(value)
    host = (parts.hostname or "").lower()
    if host.startswith("www."):
        host = host[4:]
    path = parts.path.rstrip("/") or "/"
    return f"{parts.scheme.lower()}://{host}{path}"


def normalize_domain(value: str | None) -> str | None:
    if not value:
        return None
    candidate = value if "://" in value else f"https://{value}"
    return (urlsplit(candidate).hostname or value).lower().removeprefix("www.")


def normalize_location(value: str | None) -> str | None:
    value = normalize_text(value)
    return LOCATION_ALIASES.get(value, value) if value else None


def normalize_date(value: str | None) -> str | None:
    if not value:
        return None
    value = value.strip()
    if re.fullmatch(r"\d{4}", value):
        return value
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date().isoformat()
    except ValueError:
        return value
