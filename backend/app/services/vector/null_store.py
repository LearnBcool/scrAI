from __future__ import annotations

from app.protocols.vector_store import VectorHit
from app.schemas.lead import Lead


class NullStore:
    """No-op vector store (default when VECTOR_DB_ENABLED=false)."""

    async def add_facts(self, job_id: str, leads: list[Lead]) -> None:
        return None

    async def query_facts(self, query: str, k: int = 5) -> list[VectorHit]:
        return []

    def close(self) -> None:
        return None
