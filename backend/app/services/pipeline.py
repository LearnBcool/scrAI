from __future__ import annotations

import asyncio
import logging
from typing import Awaitable, Callable

from app.agents.orchestrator import SearchOrchestrator
from app.config import settings
from app.core.jobs import JobRegistry
from app.protocols.crawler import CrawlerProvider
from app.protocols.search import SearchProvider
from app.protocols.vector_store import VectorStore
from app.repositories.lead_repo import LeadRepository
from app.repositories.vector_repo import VectorRepository
from app.schemas.search import SearchRequest
from app.services.lead_service import LeadService

logger = logging.getLogger(__name__)

STAGE_PROGRESS: dict[str, float] = {
    "parsing": 0.05,
    "searching": 0.15,
    "crawling": 0.50,
    "extracting": 0.80,
    "validating": 0.90,
    "synthesizing": 0.95,
    "done": 1.0,
}

StageCallback = Callable[[str, str], Awaitable[None]]


async def run(
    job_id: str,
    *,
    registry: JobRegistry | None = None,
    lead_repo: LeadRepository | None = None,
    search_provider: SearchProvider | None = None,
    crawler: CrawlerProvider | None = None,
    vector_store: VectorStore | None = None,
) -> None:
    """State-machine driver for a search job (background task)."""
    # Lazy fallbacks (normally the API route injects these via Depends).
    if registry is None:
        from app.api.deps import get_job_registry

        registry = get_job_registry()
    if lead_repo is None:
        from app.api.deps import get_lead_repo

        lead_repo = get_lead_repo()
    if search_provider is None:
        from app.api.deps import get_search_provider

        search_provider = get_search_provider()
    if crawler is None:
        from app.api.deps import get_crawler

        crawler = get_crawler()
    if vector_store is None:
        from app.api.deps import get_vector_store

        vector_store = get_vector_store()

    await registry.update(
        job_id,
        status="running",
        stage="parsing",
        progress=STAGE_PROGRESS["parsing"],
        message="Iniciando prospecção...",
    )

    async def on_stage(stage: str, message: str) -> None:
        progress = STAGE_PROGRESS.get(stage, 0.5)
        await registry.update(
            job_id,
            stage=stage,
            progress=progress,
            message=message,
        )

    try:
        request_data = await registry.get_request(job_id)
        if not request_data:
            raise RuntimeError("Dados da requisição não encontrados para o job.")
        request = SearchRequest.model_validate(request_data)

        orchestrator = SearchOrchestrator(
            job_id=job_id,
            search_provider=search_provider,
            crawler=crawler,
            lead_service=LeadService(lead_repo=lead_repo),
        )
        result = await asyncio.wait_for(
            orchestrator.run(request, on_stage=on_stage),
            timeout=settings.job_timeout_s,
        )

        # lead_repo persistence already happened inside validate_and_store;
        # re-run is idempotent (UPSERT ON CONFLICT) and lets us collect facts.
        leads = lead_repo.list_by_job(job_id)
        if leads:
            lead_repo.bulk_create(leads)
            vector_repo = VectorRepository(vector_store)
            await vector_repo.store_job_facts(job_id, leads)

        if not result.ok:
            detail = "; ".join(result.errors) or "Nenhum lead válido foi obtido."
            await registry.update(
                job_id,
                status="failed",
                stage="done",
                progress=1.0,
                message="Nenhum lead válido foi obtido.",
                error=detail,
            )
            return

        if result.accepted > 0:
            await registry.update(
                job_id,
                status="completed",
                stage="done",
                progress=1.0,
                message=f"Prospecção concluída com {result.accepted} lead(s).",
                lead_count=result.accepted,
            )
        else:
            await registry.update(
                job_id,
                status="partial",
                stage="done",
                progress=1.0,
                message="Prospecção concluída, mas nenhum lead foi encontrado.",
            )
    except asyncio.TimeoutError:
        await registry.update(
            job_id,
            status="failed",
            stage="done",
            progress=1.0,
            message="Prospecção expirou.",
            error=f"Tempo limite de {settings.job_timeout_s}s excedido.",
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("Pipeline falhou para o job %s", job_id)
        await registry.update(
            job_id,
            status="failed",
            stage="done",
            progress=1.0,
            message="A prospecção falhou.",
            error=f"Erro durante a prospecção: {exc}",
        )
