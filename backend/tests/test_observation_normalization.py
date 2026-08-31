from app.evidence_pipeline.extraction.normalization import canonical_predicate


def test_location_predicates_are_canonicalized() -> None:
    assert canonical_predicate("locatedIn") == "location"
    assert canonical_predicate("is based in") == "location"
    assert canonical_predicate("hasLocation") == "location"


def test_unknown_predicates_are_preserved() -> None:
    assert canonical_predicate("collaborates with") == "collaborates with"
