from __future__ import annotations

import asyncio
import logging
import time

from duckduckgo_search import DDGS

from app.protocols.search import SearchProvider
from app.schemas.tools import WebResult

logger = logging.getLogger(__name__)


class DDGSearchProvider:
    """DuckDuckGo search provider backed by the duckduckgo-search package."""

    async def search(self, query: str, max_results: int) -> list[WebResult]:
        return await asyncio.to_thread(self._search_sync, query, max_results)

    def _search_sync(self, query: str, max_results: int) -> list[WebResult]:
        last_error: Exception | None = None
        for attempt in range(3):
            try:
                rows = DDGS().text(keywords=query, max_results=max_results)
                results: list[WebResult] = []
                for rank, row in enumerate(rows, start=1):
                    url = row.get("href") or row.get("url") or ""
                    if not url:
                        continue
                    results.append(
                        WebResult(
                            url=url,
                            title=row.get("title"),
                            snippet=row.get("body"),
                            rank=rank,
                        )
                    )
                return results
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                if attempt < 2:
                    time.sleep(1.0 * (2**attempt))
        logger.warning("DDG search failed for %r: %s", query, last_error)
        raise RuntimeError(f"Falha na busca DuckDuckGo: {last_error}") from last_error
