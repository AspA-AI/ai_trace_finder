from app.evidence_pipeline.contracts.inputs import PersonClues
from app.evidence_pipeline.contracts.search import SearchQuery
from app.evidence_pipeline.retrieval.relevance import PLACEHOLDERS


class QueryPlanner:
    """Creates bounded queries from supplied clues without inventing facts."""

    def plan(self, clues: PersonClues) -> list[SearchQuery]:
        queries: list[SearchQuery] = []
        if clues.name and clues.name.lower() not in PLACEHOLDERS:
            queries.append(SearchQuery(query=f'"{clues.name}"', rationale="exact supplied name"))
            if clues.occupation or clues.locations:
                terms = [clues.occupation, *clues.locations]
                queries.append(
                    SearchQuery(
                        query=" ".join([f'"{clues.name}"', *(x for x in terms if x)]),
                        rationale="name with supplied role/location clues",
                    )
                )
        for username in [*clues.usernames, clues.github_handle]:
            if username and username.lower() not in PLACEHOLDERS:
                queries.append(SearchQuery(query=username, rationale="supplied username"))
        return queries

    def follow_up(self, clues: PersonClues, existing_queries: set[str]) -> list[SearchQuery]:
        """Create a small second set of queries without adding new facts."""
        candidates: list[SearchQuery] = []
        if clues.name and clues.github_handle:
            candidates.append(
                SearchQuery(query=f'"{clues.name}" {clues.github_handle}', rationale="name and supplied handle")
            )
        if clues.name and clues.employers:
            for employer in clues.employers:
                candidates.append(
                    SearchQuery(query=f'"{clues.name}" "{employer}"', rationale="name and supplied employer")
                )
        return [query for query in candidates if query.query not in existing_queries]
