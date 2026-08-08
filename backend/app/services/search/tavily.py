from __future__ import annotations

import httpx

from app.config import settings
from app.protocols.search import SearchProvider
from app.schemas.tools import WebResult


class TavilySearchProvider:
    """Tavily Search API client (thin httpx implementation)."""

    def __init__(self, api_key: str | None = None) -> None:
        self._api_key = api_key or settings.tavily_api_key or ""

    async def search(self, query: str, max_results: int) -> list[WebResult]:
        if not self._api_key:
            raise RuntimeError("TAVILY_API_KEY não configurada.")
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": self._api_key,
                    "query": query,
                    "max_results": min(max_results, 20),
                },
            )
            resp.raise_for_status()
        data = resp.json()
        results: list[WebResult] = []
        for rank, item in enumerate(data.get("results", []), start=1):
            url = item.get("url") or ""
            if not url:
                continue
            results.append(
                WebResult(
                    url=url,
                    title=item.get("title"),
                    snippet=item.get("content"),
                    rank=rank,
                )
            )
        return results
