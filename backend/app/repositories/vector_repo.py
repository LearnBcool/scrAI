from __future__ import annotations

from app.protocols.vector_store import VectorStore
from app.schemas.lead import Lead

DUPLICATE_THRESHOLD = 0.85


class VectorRepository:
    """High-level operations over the vector store."""

    def __init__(self, store: VectorStore) -> None:
        self._store = store

    async def store_job_facts(self, job_id: str, leads: list[Lead]) -> None:
        await self._store.add_facts(job_id, leads)

    async def find_duplicates(self, lead: Lead) -> bool:
        """Top-1 vector query; similar hit from a different job flags a duplicate."""
        query = f"{lead.name} {lead.segment or ''} {lead.city or ''}"
        hits = await self._store.query_facts(query, k=1)
        if not hits:
            return False
        hit = hits[0]
        if hit.job_id == lead.job_id:
            return False
        return hit.distance <= DUPLICATE_THRESHOLD
