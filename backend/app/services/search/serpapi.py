from __future__ import annotations

import httpx

from app.config import settings
from app.protocols.search import SearchProvider
from app.schemas.tools import WebResult


class SerpAPISearchProvider:
    """SerpAPI (Google SERP) client — thin httpx implementation."""

    def __init__(self, api_key: str | None = None) -> None:
        self._api_key = api_key or settings.serpapi_api_key or ""

    async def search(self, query: str, max_results: int) -> list[WebResult]:
        if not self._api_key:
            raise RuntimeError("SERPAPI_API_KEY não configurada.")
        params = {
            "api_key": self._api_key,
            "engine": "google",
            "q": query,
            "num": min(max_results, 20),
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get("https://serpapi.com/search.json", params=params)
            resp.raise_for_status()
        data = resp.json()
        results: list[WebResult] = []
        for rank, item in enumerate(data.get("organic_results", []), start=1):
            url = item.get("link") or ""
            if not url:
                continue
            results.append(
                WebResult(
                    url=url,
                    title=item.get("title"),
                    snippet=item.get("snippet"),
                    rank=rank,
                )
            )
        return results
