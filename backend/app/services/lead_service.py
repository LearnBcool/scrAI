from __future__ import annotations

import logging
import re

from app.core.scoring import score_confidence
from app.protocols.crawler import CrawledPage
from app.repositories.lead_repo import LeadRepository
from app.schemas.lead import Lead
from app.schemas.tools import LeadDraft
from app.services.extraction.contact_extractor import extract_contacts
from app.utils.text import extract_domain

logger = logging.getLogger(__name__)

_H1_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)


class LeadService:
    """Builds LeadDraft from crawled pages and validates/persists leads."""

    def __init__(self, lead_repo: LeadRepository) -> None:
        self._lead_repo = lead_repo

    def build_lead(
        self,
        url: str,
        page: CrawledPage,
        segment_hint: str | None = None,
    ) -> LeadDraft:
        if not page.ok:
            return LeadDraft(
                name="unknown",
                source_url=url,
                notes=page.error or "Página não pôde ser acessada.",
                confidence=0.0,
            )
        contacts = extract_contacts(page.text)
        name = (page.title or "").strip() or _extract_h1(page.text) or "unknown"
        website = self._resolve_website(url, contacts.website)
        confidence = score_confidence(
            has_name=bool(name and name != "unknown"),
            email_count=len(contacts.emails),
            phone_count=len(contacts.phones),
            whatsapp_count=len(contacts.whatsapp),
            website=website,
            social_count=sum(
                1
                for value in (contacts.instagram, contacts.linkedin, contacts.facebook)
                if value
            ),
        )
        return LeadDraft(
            name=name,
            segment=segment_hint,
            website=website,
            emails=contacts.emails,
            phones=contacts.phones,
            whatsapp=contacts.whatsapp,
            social={
                "instagram": contacts.instagram,
                "linkedin": contacts.linkedin,
                "facebook": contacts.facebook,
            },
            source_url=url,
            confidence=confidence,
        )

    def validate_and_store(
        self,
        job_id: str,
        drafts: list[LeadDraft],
    ) -> tuple[list[Lead], list[str]]:
        from app.project.lead import merge_drafts

        accepted: list[Lead] = []
        errors: list[str] = []

        merged = merge_drafts(drafts)
        for draft in merged:
            if not draft.name or not draft.name.strip():
                errors.append(f"Lead rejeitado: nome vazio (fonte: {draft.source_url})")
                continue
            if not draft.source_url:
                errors.append(f"Lead rejeitado: URL de origem ausente ({draft.name})")
                continue
            try:
                lead = Lead.model_validate(
                    {**draft.model_dump(), "job_id": job_id}
                )
            except Exception as exc:  # noqa: BLE001 (pydantic.ValidationError)
                errors.append(f"Lead '{draft.name}' rejeitado: {exc}")
                continue
            accepted.append(lead)

        if accepted:
            self._lead_repo.bulk_create(accepted)
        return accepted, errors

    @staticmethod
    def _resolve_website(source_url: str, extracted: str | None) -> str | None:
        source_domain = extract_domain(source_url)
        if extracted:
            extracted_domain = extract_domain(extracted)
            if extracted_domain and source_domain and extracted_domain != source_domain:
                return extracted
            if extracted_domain == source_domain:
                return extracted
            if not source_domain:
                return extracted
        return source_url


def _extract_h1(text: str) -> str | None:
    match = _H1_RE.search(text or "")
    if match:
        return match.group(1).strip()
    return None
