import re
from urllib.parse import unquote, urlsplit

from pydantic import BaseModel, Field

from app.evidence_pipeline.contracts.evidence import Observation
from app.evidence_pipeline.normalization.values import (
    normalize_date,
    normalize_domain,
    normalize_location,
    normalize_name,
    normalize_text,
    normalize_url,
    normalize_username,
)


class NormalizedObservation(BaseModel):
    observation_id: str
    source_id: str
    predicate: str
    original_subject: str | None = None
    original_object: str | None = None
    normalized_subject: str | None = None
    normalized_object: str | None = None
    quote: str | None = None
    source_url: str
    source_domain: str = ""
    source_platform: str = "unknown"
    source_identifiers: list[str] = Field(default_factory=list)
    object_type: str | None = None
    valid_from: str | None = None
    valid_until: str | None = None
    observed_at: str | None = None
    source_published_at: str | None = None


def normalize_observation(observation: Observation | NormalizedObservation) -> NormalizedObservation:
    if isinstance(observation, NormalizedObservation):
        return observation
    predicate = observation.predicate.lower().replace(" ", "_")
    subject = normalize_name(observation.subject_text)
    object_value = observation.object_text
    if predicate in {"location", "located_in", "is_located_in"}:
        normalized_object = normalize_location(object_value)
    elif "url" in predicate or "link" in predicate or "website" in predicate:
        normalized_object = normalize_url(object_value)
    elif "username" in predicate or "handle" in predicate or "github" in predicate:
        normalized_object = normalize_username(object_value)
    elif "domain" in predicate:
        normalized_object = normalize_domain(object_value)
    elif "date" in predicate or "founded" in predicate:
        normalized_object = normalize_date(object_value)
    else:
        normalized_object = normalize_text(object_value)
    source_url = str(observation.source_url)
    parsed = urlsplit(source_url)
    domain = (parsed.hostname or "").lower().removeprefix("www.")
    platform = {
        "github.com": "github",
        "linkedin.com": "linkedin",
        "twine.net": "twine",
        "platform.ultralytics.com": "ultralytics",
    }.get(domain, domain or "unknown")
    path_parts = [unquote(item).lower() for item in parsed.path.split("/") if item]
    generic_parts = {"profile", "profiles", "user", "users", "people", "person", "posts", "post", "activity", "activities", "in"}
    source_identifiers = [item for item in path_parts if item not in generic_parts and len(item) >= 3]
    if platform == "linkedin" and source_identifiers:
        source_identifiers[0] = re.split(r"-(?=\d)", source_identifiers[0])[0]
    source_identifiers = [item for item in source_identifiers if item]
    return NormalizedObservation(
        observation_id=observation.observation_id,
        source_id=observation.source_id,
        predicate=observation.predicate,
        original_subject=observation.subject_text,
        original_object=observation.object_text,
        normalized_subject=subject,
        normalized_object=normalized_object,
        quote=observation.quote,
        source_url=source_url,
        source_domain=domain,
        source_platform=platform,
        source_identifiers=source_identifiers,
        object_type=observation.object_type,
        valid_from=observation.valid_from.isoformat() if observation.valid_from else None,
        valid_until=observation.valid_until.isoformat() if observation.valid_until else None,
        observed_at=observation.observed_at.isoformat() if observation.observed_at else None,
        source_published_at=observation.source_published_at.isoformat() if observation.source_published_at else None,
    )
