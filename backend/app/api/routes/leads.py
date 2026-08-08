from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_job_registry, get_lead_repo
from app.core.jobs import JobRegistry
from app.repositories.lead_repo import LeadRepository
from app.schemas.lead import Lead, LeadList, utcnow

router = APIRouter(tags=["leads"])


@router.get("/leads", response_model=LeadList)
async def list_leads(
    job_id: str | None = Query(None),
    segment: str | None = Query(None),
    city: str | None = Query(None),
    q: str | None = Query(None),
    lead_repo: LeadRepository = Depends(get_lead_repo),
    registry: JobRegistry = Depends(get_job_registry),
) -> LeadList:
    leads = lead_repo.list(job_id=job_id, segment=segment, city=city, q=q)
    query = ""
    if job_id:
        job = await registry.get(job_id)
        if job is not None:
            query = job.query
    return LeadList(
        job_id=job_id or "",
        query=query,
        leads=leads,
        generated_at=utcnow(),
        total=len(leads),
    )


@router.get("/leads/{lead_id}", response_model=Lead)
async def get_lead(
    lead_id: str,
    lead_repo: LeadRepository = Depends(get_lead_repo),
) -> Lead:
    lead = lead_repo.get_by_id(lead_id)
    if lead is None:
        raise HTTPException(status_code=404, detail=f"Lead '{lead_id}' não encontrado.")
    return lead
