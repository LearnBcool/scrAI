from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.lead import utcnow

JobState = Literal["queued", "running", "completed", "partial", "failed"]
JobStage = Literal[
    "parsing",
    "searching",
    "crawling",
    "extracting",
    "validating",
    "synthesizing",
    "done",
]


class JobStatus(BaseModel):
    id: str
    status: JobState = "queued"
    stage: JobStage | None = None
    progress: float = Field(0.0, ge=0, le=1)
    message: str | None = None
    lead_count: int = 0
    error: str | None = None
    query: str = ""
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
