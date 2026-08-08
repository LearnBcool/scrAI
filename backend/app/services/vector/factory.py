from __future__ import annotations

from app.config import settings
from app.protocols.vector_store import VectorStore


def get_vector_store() -> VectorStore:
    if settings.vector_db_enabled:
        # Lazy import so chromadb is only loaded when actually enabled.
        from app.services.vector.chroma_store import ChromaStore

        return ChromaStore(path=settings.chroma_dir)
    from app.services.vector.null_store import NullStore

    return NullStore()
