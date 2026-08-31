from app.evidence_pipeline.contracts.inputs import PersonClues
from app.evidence_pipeline.retrieval.relevance import assess_relevance


def test_rejects_topic_only_source_for_named_person() -> None:
    result = assess_relevance(
        PersonClues(name="Rehmet Yeshanew", occupation="AI Developer", locations=["Austria"]),
        url="https://ai-at.eu/en",
        title="AI Factory Austria",
        text="AI Factory Austria provides supercomputing and training.",
    )
    assert result.relevant is False


def test_accepts_source_that_names_target() -> None:
    result = assess_relevance(
        PersonClues(name="Rehmet Yeshanew", occupation="AI Developer"),
        url="https://example.com/rehmet-yeshanew",
        title="Rehmet Yeshanew portfolio",
        text="Rehmet Yeshanew develops AI applications.",
    )
    assert result.relevant is True
