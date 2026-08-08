from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from app.schemas.lead import Lead


@dataclass
class VectorHit:
    lead_id: str
    job_id: str
    document: str
    distance: float


@runtime_checkable
class VectorStore(Protocol):
    async def add_facts(self, job_id: str, leads: list[Lead]) -> None: ...

    async def query_facts(self, query: str, k: int = 5) -> list[VectorHit]: ...

    def close(self) -> None: ...
