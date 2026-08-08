from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Any

from app.schemas.job import JobStatus
from app.schemas.lead import utcnow

_TTL = timedelta(hours=24)


class JobRegistry:
    """In-memory registry of search jobs with 24h TTL cleanup."""

    def __init__(self) -> None:
        self._jobs: dict[str, JobStatus] = {}
        self._requests: dict[str, dict[str, Any]] = {}
        self._lock = asyncio.Lock()

    async def create(self, metadata: dict[str, Any]) -> str:
        job_id = str(uuid.uuid4())
        request = dict(metadata.get("request") or {})
        job = JobStatus(
            id=job_id,
            status="queued",
            stage=None,
            progress=0.0,
            message="Job enfileirado.",
            query=str(metadata.get("query") or request.get("query") or ""),
        )
        async with self._lock:
            self._jobs[job_id] = job
            self._requests[job_id] = request
        return job_id

    async def update(self, job_id: str, **fields: Any) -> JobStatus | None:
        async with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                return None
            updated = job.model_copy(update=fields)
            updated.updated_at = utcnow()
            self._jobs[job_id] = updated
            return updated

    async def get(self, job_id: str) -> JobStatus | None:
        async with self._lock:
            return self._jobs.get(job_id)

    async def get_request(self, job_id: str) -> dict[str, Any] | None:
        async with self._lock:
            return self._requests.get(job_id)

    async def list(self, limit: int = 20) -> list[JobStatus]:
        async with self._lock:
            self._purge_expired()
            jobs = sorted(
                self._jobs.values(),
                key=lambda job: job.created_at,
                reverse=True,
            )
            return jobs[:limit]

    async def clear(self) -> None:
        async with self._lock:
            self._jobs.clear()
            self._requests.clear()

    def _purge_expired(self) -> None:
        now = datetime.now(utcnow().tzinfo)
        expired = [
            job_id
            for job_id, job in self._jobs.items()
            if now - job.created_at > _TTL
        ]
        for job_id in expired:
            self._jobs.pop(job_id, None)
            self._requests.pop(job_id, None)


_registry: JobRegistry | None = None


def get_registry() -> JobRegistry:
    """Module-level default registry singleton."""
    global _registry
    if _registry is None:
        _registry = JobRegistry()
    return _registry
