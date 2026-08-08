from __future__ import annotations

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str
    segment: str | None = None
    city: str | None = None
    state: str | None = None
    max_leads: int = Field(10, ge=1, le=50)
    max_pages: int | None = Field(None, ge=1, le=50)


class SearchResponse(BaseModel):
    job_id: str
    status_url: str
