from app.evidence_pipeline.contracts.inputs import PersonClues
from app.evidence_pipeline.discovery.query_planner import QueryPlanner


def test_query_planner_uses_only_supplied_clues() -> None:
    queries = QueryPlanner().plan(
        PersonClues(name="Jane Doe", occupation="Researcher", locations=["Vienna"])
    )

    assert [q.query for q in queries] == ['"Jane Doe"', '"Jane Doe" Researcher Vienna']
