from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.lead import utcnow

OutreachChannel = Literal["email", "whatsapp"]


class OutreachChoice(BaseModel):
    job_id: str
    channel: OutreachChannel
    lead_ids: list[str] = Field(default_factory=list)
    template: str | None = None


class OutreachRecipient(BaseModel):
    lead_id: str
    name: str
    contact: str
    message: str


class OutreachPlan(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    job_id: str
    channel: OutreachChannel
    recipients: list[OutreachRecipient] = Field(default_factory=list)
    message_template: str
    status: Literal["draft", "scheduled", "sent"] = "draft"
    created_at: datetime = Field(default_factory=utcnow)


class OutreachSendResult(BaseModel):
    plan_id: str
    delivered: int = 0
    stub: bool = True
    message: str = ""
