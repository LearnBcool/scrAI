from __future__ import annotations

from app.core.scoring import (
    canonical_domain,
    canonical_email,
    canonical_phone,
    dedup_keys,
    score_confidence,
)
from app.project.lead import merge_drafts
from app.schemas.tools import LeadDraft


def test_canonical_keys():
    assert canonical_email("  Contato@Acme.COM  ") == "contato@acme.com"
    assert canonical_phone("(11) 91234-5678") == "11912345678"
    assert canonical_phone("+55 11 98765-4321") == "11987654321"
    assert canonical_domain("https://www.Acme.com.br/") == "acme.com.br"
    assert canonical_domain("acme.com.br") == "acme.com.br"
    assert canonical_domain(None) is None


def test_dedup_keys():
    keys = dedup_keys(
        website="https://acme.com",
        emails=["contato@acme.com"],
        phones=["(11) 91234-5678"],
    )
    assert "email:contato@acme.com" in keys
    assert "phone:11912345678" in keys
    assert "domain:acme.com" in keys


def test_dedup_keys_whatsapp():
    keys = dedup_keys(whatsapp=["https://wa.me/5511912345678"])
    assert "wa:11912345678" in keys


def test_confidence_bounds():
    scores = [
        score_confidence(has_name=True, email_count=3, phone_count=2, whatsapp_count=1, website="https://x.com", social_count=3),
        score_confidence(has_name=False, email_count=0, phone_count=0, whatsapp_count=0, website=None, social_count=0),
        score_confidence(has_name=True, email_count=10, phone_count=10, whatsapp_count=10, website="https://x.com", social_count=10),
    ]
    for score in scores:
        assert 0.0 <= score <= 1.0
    # stronger signal -> higher score
    assert scores[2] >= scores[0] >= scores[1]
    assert scores[2] == 1.0  # capped


def test_merge_drafts_dedup_by_email():
    a = LeadDraft(
        name="Acme",
        emails=["contato@acme.com"],
        source_url="https://acme.com",
        confidence=0.4,
    )
    b = LeadDraft(
        name="Acme Ltda",
        emails=["CONTATO@acme.com"],
        phones=["11912345678"],
        source_url="https://acme.com",
        confidence=0.8,
    )
    merged = merge_drafts([a, b])
    assert len(merged) == 1
    m = merged[0]
    assert m.name == "Acme Ltda"  # highest confidence wins
    assert "contato@acme.com" in m.emails
    assert "11912345678" in m.phones
    assert m.confidence == 0.8


def test_merge_drafts_dedup_by_domain():
    a = LeadDraft(name="A", website="https://acme.com", source_url="https://acme.com/contato")
    b = LeadDraft(name="B", website="https://www.acme.com", source_url="https://acme.com/sobre")
    merged = merge_drafts([a, b])
    assert len(merged) == 1


def test_merge_drafts_keeps_distinct():
    a = LeadDraft(name="A", emails=["a@x.com"], source_url="https://a.com")
    b = LeadDraft(name="B", emails=["b@y.com"], source_url="https://b.com")
    merged = merge_drafts([a, b])
    assert len(merged) == 2


def test_merge_drafts_empty():
    assert merge_drafts([]) == []
