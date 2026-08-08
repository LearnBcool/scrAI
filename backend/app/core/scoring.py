from __future__ import annotations

from typing import Iterable
from urllib.parse import urlparse

from app.utils.validators import normalize_email, normalize_phone


def canonical_email(email: str) -> str:
    norm = normalize_email(email)
    return norm if norm else (email or "").strip().lower()


def canonical_phone(phone: str) -> str:
    norm = normalize_phone(phone)
    return norm if norm else "".join(ch for ch in (phone or "") if ch.isdigit())


def canonical_domain(url: str | None) -> str | None:
    if not url:
        return None
    value = url if "://" in url else f"https://{url}"
    try:
        netloc = urlparse(value).netloc.lower()
    except ValueError:
        return None
    if netloc.startswith("www."):
        netloc = netloc[4:]
    return netloc or None


def dedup_keys(
    *,
    website: str | None = None,
    emails: Iterable[str] = (),
    phones: Iterable[str] = (),
    whatsapp: Iterable[str] = (),
) -> set[str]:
    """Canonical identity keys used to detect duplicates across leads."""
    keys: set[str] = set()
    for email in emails:
        clean = canonical_email(email)
        if clean:
            keys.add(f"email:{clean}")
    for phone in phones:
        clean = canonical_phone(phone)
        if clean:
            keys.add(f"phone:{clean}")
    for wa in whatsapp:
        clean = canonical_phone(wa)
        if clean:
            keys.add(f"wa:{clean}")
    domain = canonical_domain(website)
    if domain:
        keys.add(f"domain:{domain}")
    return keys


def score_confidence(
    *,
    has_name: bool,
    email_count: int,
    phone_count: int,
    whatsapp_count: int,
    website: str | None,
    social_count: int = 0,
) -> float:
    """Blend signal presence into a confidence score in [0, 1]."""
    score = 0.0
    if has_name:
        score += 0.30
    if website:
        score += 0.15
    score += min(0.25, 0.08 * max(0, email_count))
    score += min(0.20, 0.06 * max(0, phone_count))
    score += min(0.15, 0.07 * max(0, whatsapp_count))
    score += min(0.10, 0.03 * max(0, social_count))
    return round(min(1.0, score), 2)
