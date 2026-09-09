from app.evidence_pipeline.contracts.search import SearchQuery
from app.evidence_pipeline.retrieval.relevance import PLACEHOLDERS
from app.business_investigation.contracts import BusinessClues


class BusinessQueryPlanner:
    """Bounded business queries using only supplied company clues."""

    def plan(self, clues: BusinessClues) -> list[SearchQuery]:
        queries: list[SearchQuery] = []
        name = clues.company_name.strip()
        if name and name.lower() not in PLACEHOLDERS:
            queries.append(SearchQuery(query=f'"{name}"', rationale="exact supplied company name"))
            context = [clues.industry, *clues.locations, *clues.products]
            terms = [item for item in context if item and item.lower() not in PLACEHOLDERS]
            if terms:
                queries.append(SearchQuery(query=" ".join([f'"{name}"', *terms]), rationale="company with supplied business context"))
        for domain in clues.domains:
            if domain and domain.lower() not in PLACEHOLDERS:
                queries.append(SearchQuery(query=domain, rationale="supplied company domain"))
        for person in [*clues.founders, *clues.executives]:
            if person and person.lower() not in PLACEHOLDERS:
                queries.append(SearchQuery(query=f'"{name}" "{person}"', rationale="supplied company relationship"))
        return queries

    def follow_up(self, clues: BusinessClues, existing_queries: set[str]) -> list[SearchQuery]:
        candidates = [
            SearchQuery(query=f'"{clues.company_name}" founders', rationale="company founder discovery"),
            SearchQuery(query=f'"{clues.company_name}" products', rationale="company product discovery"),
        ]
        return [item for item in candidates if item.query not in existing_queries]
