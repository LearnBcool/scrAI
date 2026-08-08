from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.config import settings
from app.models.db import init_db

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()

    from app.core.jobs import get_registry

    registry = get_registry()

    from app.services.vector.factory import get_vector_store

    app.state.vector_store = get_vector_store()

    from app.services.crawler.factory import get_crawler

    app.state.crawler = get_crawler()

    app.state.tasks = set()
    yield

    # Shutdown cleanup
    for task in list(getattr(app.state, "tasks", set())):
        task.cancel()
    await registry.clear()
    store = getattr(app.state, "vector_store", None)
    if store is not None:
        try:
            store.close()
        except Exception:  # noqa: BLE001
            logger.exception("Falha ao fechar o vector store")


app = FastAPI(title="scrapAI", version="0.1.0", lifespan=lifespan)

origins = [
    origin.strip()
    for origin in settings.cors_origins.split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/")
def root():
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": "0.1.0",
        "message": "Backend is running.",
    }
