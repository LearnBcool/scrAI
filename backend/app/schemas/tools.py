from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.lead import ContactInfo


class WebResult(BaseModel):
    url: str
    title: str | None = None
    snippet: str | None = None
    rank: int = 0


class SearchWebInput(BaseModel):
    query: str
    max_results: int = 10


class SearchWebOutput(BaseModel):
    query: str
    results: list[WebResult] = Field(default_factory=list)


class CrawlUrlInput(BaseModel):
    url: str
    js: bool = False


class CrawlUrlOutput(BaseModel):
    url: str
    ok: bool
    title: str | None = None
    text_preview: str | None = None
    email_hits: int = 0
    phone_hits: int = 0
    needed_js: bool = False
    error: str | None = None


class ExtractContactsInput(BaseModel):
    url: str
    js_rerun: bool = False


class ExtractContactsOutput(BaseModel):
    url: str
    ok: bool
    name: str | None = None
    segment: str | None = None
    city: str | None = None
    contacts: ContactInfo = Field(default_factory=ContactInfo)
    confidence: float = 0.0
    error: str | None = None


class LeadDraft(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str
    segment: str | None = None
    city: str | None = None
    state: str | None = None
    website: str | None = None
    emails: list[str] = Field(default_factory=list)
    phones: list[str] = Field(default_factory=list)
    whatsapp: list[str] = Field(default_factory=list)
    social: dict[str, str | None] = Field(default_factory=dict)
    source_url: str
    confidence: float = Field(0.0, ge=0, le=1)
    notes: str | None = None


class FinalizeInput(BaseModel):
    summary: str
    leads: list[LeadDraft] = Field(default_factory=list)


class FinalizeOutput(BaseModel):
    ok: bool
    accepted: int = 0
    rejected: int = 0
    errors: list[str] = Field(default_factory=list)
