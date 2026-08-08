from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.deps import get_outreach_service
from app.schemas.outreach import (
    OutreachChoice,
    OutreachPlan,
    OutreachSendResult,
)
from app.services.outreach_service import OutreachService

router = APIRouter(tags=["outreach"])


class SendPlanRequest(BaseModel):
    plan_id: str


class OutreachChoiceResponse(BaseModel):
    plan: OutreachPlan


@router.post("/outreach/choose", response_model=OutreachChoiceResponse)
async def choose_outreach(
    choice: OutreachChoice,
    service: OutreachService = Depends(get_outreach_service),
) -> OutreachChoiceResponse:
    try:
        plan = service.build_plan(
            job_id=choice.job_id,
            channel=choice.channel,
            lead_ids=choice.lead_ids,
            template=choice.template,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return OutreachChoiceResponse(plan=plan)


@router.post("/outreach/send", response_model=OutreachSendResult)
async def send_outreach(
    payload: SendPlanRequest,
    service: OutreachService = Depends(get_outreach_service),
) -> OutreachSendResult:
    return service.send(payload.plan_id)


@router.get("/outreach/plans/{plan_id}", response_model=OutreachPlan)
async def get_plan(
    plan_id: str,
    service: OutreachService = Depends(get_outreach_service),
) -> OutreachPlan:
    plan = service.load_plan(plan_id)
    if plan is None:
        raise HTTPException(
            status_code=404,
            detail=f"Plano de outreach '{plan_id}' não encontrado.",
        )
    return plan
