from datetime import datetime, timezone
from hashlib import sha256
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from app.evidence_pipeline.contracts.evidence import RawSource, SourceType
from app.evidence_pipeline.retrieval.safety import (
    MAX_REDIRECTS,
    MAX_RESPONSE_BYTES,
    UnsafeUrlError,
    assert_public_http_url,
)


class WebPageRetriever:
    name = "direct_http"

    def __init__(self, timeout: float = 20.0, max_bytes: int = MAX_RESPONSE_BYTES) -> None:
        self.timeout = timeout
        self.max_bytes = max_bytes

    def supports(self, url: str) -> bool:
        try:
            assert_public_http_url(url)
        except UnsafeUrlError:
            return False
        return True

    async def fetch(self, url: str, investigation_id: str) -> RawSource:
        current = url
        response_url = url
        response_status = 0
        body = b""
        content_type = ""
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=False) as client:
            for _ in range(MAX_REDIRECTS + 1):
                assert_public_http_url(current)
                async with client.stream(
                    "GET", current, headers={"User-Agent": "PeopleInvestigation/0.1"}
                ) as response:
                    response_status = response.status_code
                    if response.is_redirect:
                        location = response.headers.get("location")
                        if not location:
                            response.raise_for_status()
                            break
                        current = urljoin(str(response.url), location)
                        continue
                    response.raise_for_status()
                    body = await _read_limited(response, self.max_bytes)
                    response_url = str(response.url)
                    content_type = response.headers.get("content-type", "")
                    break
            else:
                raise UnsafeUrlError("too many redirects")

        encoding = "utf-8"
        charset = ""
        if "charset=" in content_type.lower():
            charset = content_type.split("charset=", 1)[-1].split(";")[0].strip()
        response_text = body.decode(charset or encoding, errors="replace").replace("\x00", "")
        soup = BeautifulSoup(response_text, "lxml")
        image_url = None
        for attrs in ({"property": "og:image"}, {"name": "twitter:image"}):
            tag = soup.find("meta", attrs=attrs)
            if tag and tag.get("content", "").startswith(("http://", "https://")):
                candidate = tag["content"]
                try:
                    assert_public_http_url(candidate)
                except UnsafeUrlError:
                    continue
                image_url = candidate
                break
        for element in soup(["script", "style", "noscript"]):
            element.decompose()
        content = "\n".join(line.strip() for line in soup.get_text("\n").splitlines() if line.strip())
        return RawSource(
            source_id=f"src_{sha256(response_url.encode()).hexdigest()[:16]}",
            investigation_id=investigation_id,
            url=url,
            canonical_url=response_url,
            source_type=SourceType.WEBPAGE,
            domain=urlparse(response_url).hostname or "",
            retrieval_method=self.name,
            http_status=response_status,
            retrieved_at=datetime.now(timezone.utc),
            raw_content=response_text,
            content=content,
            content_hash=sha256(content.encode()).hexdigest(),
            provider=self.name,
            metadata={"image_url": image_url} if image_url else {},
        )


async def _read_limited(response: httpx.Response, max_bytes: int) -> bytes:
    content_length = response.headers.get("content-length")
    if content_length and content_length.isdigit() and int(content_length) > max_bytes:
        raise UnsafeUrlError("response exceeds size limit")
    chunks: list[bytes] = []
    total = 0
    async for chunk in response.aiter_bytes():
        total += len(chunk)
        if total > max_bytes:
            raise UnsafeUrlError("response exceeds size limit")
        chunks.append(chunk)
    return b"".join(chunks)
