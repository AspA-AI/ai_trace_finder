from datetime import datetime, timezone

import httpx

from app.evidence_pipeline.contracts.search import SearchResult


class TavilyDiscovery:
    name = "tavily"

    def __init__(self, api_key: str, base_url: str, timeout: float = 20.0) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def search(self, query: str, limit: int = 10) -> list[SearchResult]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/search",
                json={
                    "api_key": self.api_key,
                    "query": query,
                    "max_results": limit,
                    "include_answer": False,
                },
            )
            response.raise_for_status()
            payload = response.json()
        now = datetime.now(timezone.utc)
        return [
            SearchResult(
                url=item["url"],
                title=item.get("title"),
                snippet=item.get("content"),
                source_provider=self.name,
                discovered_at=now,
            )
            for item in payload.get("results", [])
            if item.get("url")
        ]
