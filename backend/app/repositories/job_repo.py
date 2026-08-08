from __future__ import annotations

from typing import Any

from app.core.jobs import JobRegistry
from app.schemas.job import JobStatus


class JobRepository:
    """Facade over the in-memory JobRegistry."""

    def __init__(self, registry: JobRegistry) -> None:
        self._registry = registry

    async def create(self, *, query: str, request: dict[str, Any]) -> str:
        return await self._registry.create({"query": query, "request": request})

    async def update(self, job_id: str, **fields: Any) -> JobStatus | None:
        return await self._registry.update(job_id, **fields)

    async def get(self, job_id: str) -> JobStatus | None:
        return await self._registry.get(job_id)

    async def list(self, limit: int = 20) -> list[JobStatus]:
        return await self._registry.list(limit=limit)

    async def get_request(self, job_id: str) -> dict[str, Any] | None:
        return await self._registry.get_request(job_id)
