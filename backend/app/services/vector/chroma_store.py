from __future__ import annotations

from typing import Any

import chromadb

from app.protocols.vector_store import VectorHit
from app.schemas.lead import Lead


def _flatten(lead: Lead) -> str:
    parts = [
        lead.name,
        lead.segment or "",
        lead.city or "",
        lead.state or "",
        lead.website or "",
        ", ".join(lead.emails),
        ", ".join(lead.whatsapp),
    ]
    return " | ".join(p for p in parts if p)


class ChromaStore:
    """ChromaDB-backed vector store for lead facts (collection 'lead_facts')."""

    def __init__(self, path: str, collection_name: str = "lead_facts") -> None:
        self._client = chromadb.PersistentClient(path=path)
        self._collection = self._client.get_or_create_collection(name=collection_name)

    async def add_facts(self, job_id: str, leads: list[Lead]) -> None:
        if not leads:
            return
        self._collection.add(
            ids=[lead.id for lead in leads],
            documents=[_flatten(lead) for lead in leads],
            metadatas=[
                {
                    "job_id": job_id,
                    "lead_id": lead.id,
                    "confidence": lead.confidence,
                }
                for lead in leads
            ],
        )

    async def query_facts(self, query: str, k: int = 5) -> list[VectorHit]:
        res = self._collection.query(query_texts=[query], n_results=k)
        ids = (res.get("ids") or [[]])[0] or []
        docs = (res.get("documents") or [[]])[0] or []
        dists = (res.get("distances") or [[]])[0] or []
        metas = (res.get("metadatas") or [[]])[0] or []
        hits: list[VectorHit] = []
        for index, lead_id in enumerate(ids):
            meta: dict[str, Any] = metas[index] if index < len(metas) else {}
            hits.append(
                VectorHit(
                    lead_id=lead_id,
                    job_id=str(meta.get("job_id", "")),
                    document=docs[index] if index < len(docs) else "",
                    distance=float(dists[index]) if index < len(dists) else 1.0,
                )
            )
        return hits

    def close(self) -> None:
        self._collection = None  # type: ignore[assignment]
        self._client = None  # type: ignore[assignment]
