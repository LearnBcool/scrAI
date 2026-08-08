from __future__ import annotations

import asyncio

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from app.api.deps import (
    get_crawler,
    get_job_registry,
    get_lead_repo,
    get_search_provider,
    get_vector_store,
)
from app.core.jobs import JobRegistry
from app.protocols.crawler import CrawlerProvider
from app.protocols.search import SearchProvider
from app.protocols.vector_store import VectorStore
from app.repositories.lead_repo import LeadRepository
from app.schemas.job import JobStatus
from app.schemas.search import SearchRequest, SearchResponse
from app.services import pipeline

router = APIRouter(tags=["search"])


@router.post("/search", status_code=202, response_model=SearchResponse)
async def create_search(
    request: SearchRequest,
    http_request: Request,
    registry: JobRegistry = Depends(get_job_registry),
    lead_repo: LeadRepository = Depends(get_lead_repo),
    search_provider: SearchProvider = Depends(get_search_provider),
    crawler: CrawlerProvider = Depends(get_crawler),
    vector_store: VectorStore = Depends(get_vector_store),
) -> SearchResponse:
    job_id = await registry.create(
        {"query": request.query, "request": request.model_dump()}
    )
    task = asyncio.create_task(
        pipeline.run(
            job_id,
            registry=registry,
            lead_repo=lead_repo,
            search_provider=search_provider,
            crawler=crawler,
            vector_store=vector_store,
        )
    )
    tasks = http_request.app.state.tasks
    tasks.add(task)
    task.add_done_callback(tasks.discard)
    return SearchResponse(job_id=job_id, status_url=f"/api/jobs/{job_id}")


@router.get("/jobs/{job_id}", response_model=JobStatus)
async def get_job(
    job_id: str,
    registry: JobRegistry = Depends(get_job_registry),
) -> JobStatus:
    job = await registry.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' não encontrado.")
    return job


@router.get("/jobs", response_model=list[JobStatus])
async def list_jobs(
    limit: int = Query(20, ge=1, le=100),
    registry: JobRegistry = Depends(get_job_registry),
) -> list[JobStatus]:
    return await registry.list(limit=limit)
