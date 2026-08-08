from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.schemas.tools import WebResult


@runtime_checkable
class SearchProvider(Protocol):
    async def search(self, query: str, max_results: int) -> list[WebResult]: ...
