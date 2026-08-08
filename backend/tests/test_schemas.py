from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.schemas.lead import Lead
from app.schemas.search import SearchRequest


def test_search_request_defaults():
    req = SearchRequest(query="pizzaria em são paulo")
    assert req.query == "pizzaria em são paulo"
    assert req.max_leads == 10
    assert req.max_pages is None
    assert req.segment is None


def test_search_request_optional_fields():
    req = SearchRequest(query="advogados", segment="advocacia", city="Campinas", state="SP", max_leads=5, max_pages=8)
    assert req.city == "Campinas"
    assert req.state == "SP"
    assert req.max_leads == 5
    assert req.max_pages == 8


def test_search_request_max_leads_constraints():
    with pytest.raises(ValidationError):
        SearchRequest(query="x", max_leads=0)
    with pytest.raises(ValidationError):
        SearchRequest(query="x", max_leads=51)


def test_search_request_max_pages_constraints():
    with pytest.raises(ValidationError):
        SearchRequest(query="x", max_pages=0)
    with pytest.raises(ValidationError):
        SearchRequest(query="x", max_pages=51)


def test_lead_defaults():
    lead = Lead(job_id="job-1", name="Acme")
    assert lead.status == "new"
    assert lead.confidence == 0.0
    assert lead.emails == []
    assert lead.phones == []
    assert lead.whatsapp == []
    assert lead.social == {}
    assert lead.source_url == ""
    assert lead.id  # uuid generated


def test_lead_confidence_bounds():
    with pytest.raises(ValidationError):
        Lead(job_id="job-1", name="Acme", confidence=1.5)
    with pytest.raises(ValidationError):
        Lead(job_id="job-1", name="Acme", confidence=-0.1)


def test_lead_social_dict():
    lead = Lead(job_id="job-1", name="Acme", social={"instagram": "https://instagram.com/acme"})
    assert lead.social["instagram"] == "https://instagram.com/acme"


def test_lead_requires_name():
    with pytest.raises(ValidationError):
        Lead(job_id="job-1")  # type: ignore[call-arg]
