import re

from app.evidence_pipeline.contracts.evidence import Observation


PREDICATE_ALIASES = {
    "locatedin": "location",
    "haslocation": "location",
    "islocatedin": "location",
    "isbasedin": "location",
    "worksfrom": "location",
    "location": "location",
    "hasoccupation": "occupation",
    "occupation": "occupation",
    "hasexperience": "experience",
    "experience": "experience",
    "hasskill": "skill",
    "skill": "skill",
    "hasproject": "project",
    "project": "project",
    "developed": "project",
    "built": "project",
    "created": "project",
}


def canonical_predicate(predicate: str) -> str:
    key = re.sub(r"[^a-z0-9]", "", predicate.lower())
    return PREDICATE_ALIASES.get(key, predicate.strip())


def normalize_observations(observations: list[Observation]) -> list[Observation]:
    return [item.model_copy(update={"predicate": canonical_predicate(item.predicate)}) for item in observations]
