from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ContactInfo(BaseModel):
    emails: list[str] = Field(default_factory=list)
    phones: list[str] = Field(default_factory=list)
    whatsapp: list[str] = Field(default_factory=list)
    instagram: str | None = None
    linkedin: str | None = None
    facebook: str | None = None
    website: str | None = None


class Lead(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    job_id: str
    name: str
    segment: str | None = None
    city: str | None = None
    state: str | None = None
    website: str | None = None
    emails: list[str] = Field(default_factory=list)
    phones: list[str] = Field(default_factory=list)
    whatsapp: list[str] = Field(default_factory=list)
    social: dict[str, str | None] = Field(default_factory=dict)
    confidence: float = Field(0.0, ge=0, le=1)
    source_url: str = ""
    notes: str | None = None
    created_at: datetime = Field(default_factory=utcnow)
    status: Literal["new", "contacted", "skipped"] = "new"


class LeadList(BaseModel):
    job_id: str = ""
    query: str = ""
    leads: list[Lead] = Field(default_factory=list)
    summary: str | None = None
    generated_at: datetime = Field(default_factory=utcnow)
    total: int = 0
    rejected: int = 0
