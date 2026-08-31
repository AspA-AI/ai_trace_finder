from datetime import datetime, timezone
from hashlib import sha256
from urllib.parse import urlparse

import httpx

from app.evidence_pipeline.contracts.evidence import RawSource, SourceType


class GitHubRetriever:
    name = "github_api"

    def __init__(self, token: str | None, base_url: str, timeout: float = 20.0) -> None:
        self.token = token
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def supports(self, url: str) -> bool:
        return urlparse(url).netloc.lower().endswith("github.com")

    async def fetch(self, url: str, investigation_id: str) -> RawSource:
        parsed = urlparse(url)
        segments = [part for part in parsed.path.split("/") if part]
        headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
        token = (self.token or "").strip()
        if token:
            headers["Authorization"] = token if token.lower().startswith("bearer ") else f"Bearer {token}"
        endpoint = f"{self.base_url}/users/{segments[0]}" if segments else f"{self.base_url}/users/"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(endpoint, headers=headers)
            # Public GitHub profiles remain retrievable if a configured token
            # is expired or malformed. Do not turn a bad optional credential
            # into a failure for an otherwise public source.
            if response.status_code == 401 and token:
                response = await client.get(endpoint, headers={"Accept": headers["Accept"], "X-GitHub-Api-Version": headers["X-GitHub-Api-Version"]})
            response.raise_for_status()
            content = response.text
            payload = response.json()
        return RawSource(
            source_id=f"src_{sha256(url.encode()).hexdigest()[:16]}",
            investigation_id=investigation_id,
            url=url,
            source_type=SourceType.GITHUB,
            domain="github.com",
            retrieval_method="github_api",
            http_status=response.status_code,
            retrieved_at=datetime.now(timezone.utc),
            raw_content=content,
            content=content,
            content_hash=sha256(content.encode()).hexdigest(),
            provider=self.name,
            metadata={
                "api_endpoint": endpoint,
                "authentication": "anonymous_fallback" if token and response.request.headers.get("Authorization") is None else "token" if token else "anonymous",
                **({"image_url": payload["avatar_url"]} if payload.get("avatar_url") else {}),
            },
        )
