from __future__ import annotations

from app.core.jobs import JobRegistry, get_registry
from app.protocols.crawler import CrawlerProvider
from app.protocols.search import SearchProvider
from app.protocols.vector_store import VectorStore
from app.repositories.lead_repo import LeadRepository
from app.services.crawler import factory as crawler_factory
from app.services.outreach_service import OutreachService
from app.services.search import factory as search_factory
from app.services.vector import factory as vector_factory

_lead_repo: LeadRepository | None = None
_job_registry: JobRegistry | None = None
_outreach_service: OutreachService | None = None
_cached_search: SearchProvider | None = None
_cached_crawler: CrawlerProvider | None = None
_cached_vector: VectorStore | None = None


def get_lead_repo() -> LeadRepository:
    global _lead_repo
    if _lead_repo is None:
        _lead_repo = LeadRepository()
    return _lead_repo


def get_job_registry() -> JobRegistry:
    global _job_registry
    if _job_registry is None:
        _job_registry = get_registry()
    return _job_registry


def get_search_provider() -> SearchProvider:
    global _cached_search
    if _cached_search is None:
        _cached_search = search_factory.get_search_provider()
    return _cached_search


def get_crawler() -> CrawlerProvider:
    global _cached_crawler
    if _cached_crawler is None:
        _cached_crawler = crawler_factory.get_crawler()
    return _cached_crawler


def get_vector_store() -> VectorStore:
    global _cached_vector
    if _cached_vector is None:
        _cached_vector = vector_factory.get_vector_store()
    return _cached_vector


def get_outreach_service() -> OutreachService:
    global _outreach_service
    if _outreach_service is None:
        _outreach_service = OutreachService(lead_repo=get_lead_repo())
    return _outreach_service
