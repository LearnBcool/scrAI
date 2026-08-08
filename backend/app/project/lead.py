from __future__ import annotations

from app.core.scoring import dedup_keys
from app.schemas.tools import LeadDraft


def _group_keys(group: list[LeadDraft]) -> set[str]:
    keys: set[str] = set()
    for draft in group:
        keys |= dedup_keys(
            website=draft.website,
            emails=draft.emails,
            phones=draft.phones,
            whatsapp=draft.whatsapp,
        )
    return keys


def merge_drafts(drafts: list[LeadDraft]) -> list[LeadDraft]:
    """Dedup by canonical keys, merging contact fields into the highest-confidence draft."""
    groups: list[list[LeadDraft]] = []
    for draft in sorted(drafts, key=lambda d: d.confidence, reverse=True):
        keys = dedup_keys(
            website=draft.website,
            emails=draft.emails,
            phones=draft.phones,
            whatsapp=draft.whatsapp,
        )
        target: list[LeadDraft] | None = None
        for group in groups:
            if keys and (_group_keys(group) & keys):
                target = group
                break
        if target is None:
            groups.append([draft])
        else:
            target.append(draft)
    return [_merge_group(group) for group in groups]


def _merge_group(group: list[LeadDraft]) -> LeadDraft:
    ordered = sorted(group, key=lambda d: d.confidence, reverse=True)
    base = ordered[0].model_copy(deep=True)

    emails = list(base.emails)
    phones = list(base.phones)
    whatsapp = list(base.whatsapp)
    social = dict(base.social or {})

    for draft in ordered[1:]:
        for email in draft.emails:
            if email not in emails:
                emails.append(email)
        for phone in draft.phones:
            if phone not in phones:
                phones.append(phone)
        for wa in draft.whatsapp:
            if wa not in whatsapp:
                whatsapp.append(wa)
        for key, value in (draft.social or {}).items():
            social.setdefault(key, value)
        base.segment = base.segment or draft.segment
        base.city = base.city or draft.city
        base.state = base.state or draft.state
        base.website = base.website or draft.website
        if base.notes and draft.notes:
            base.notes = f"{base.notes}\n{draft.notes}"
        elif draft.notes and not base.notes:
            base.notes = draft.notes

    base.emails = emails
    base.phones = phones
    base.whatsapp = whatsapp
    base.social = social
    return base
