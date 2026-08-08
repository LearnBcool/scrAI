from __future__ import annotations

import re

EMAIL_PATTERN = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
EMAIL_RE = re.compile(EMAIL_PATTERN)

# BR phone as digits with DDD: (10) or (11) digits, optionally prefixed by +55
PHONE_DIGITS_RE = re.compile(r"\d{10,13}")

_EMAIL_FULL_RE = re.compile(rf"^{EMAIL_PATTERN}$")
_DIGITS_ONLY_RE = re.compile(r"\d+")


def normalize_email(email: str | None) -> str | None:
    """Lowercase, trimmed email; returns None when invalid/empty."""
    if not email:
        return None
    clean = email.strip().lower()
    if not _EMAIL_FULL_RE.match(clean):
        return None
    return clean


def normalize_phone(raw: str | None) -> str | None:
    """Normalize a BR phone/WhatsApp number to digits with DDD (no country code)."""
    if not raw:
        return None
    digits = "".join(_DIGITS_ONLY_RE.findall(raw))
    if not digits:
        return None
    if digits.startswith("55") and len(digits) in (12, 13):
        digits = digits[2:]
    if len(digits) not in (10, 11):
        return None
    return digits


def build_wa_link(raw: str | None) -> str | None:
    """Build a wa.me link from a raw number or an existing WhatsApp link/number."""
    if not raw:
        return None
    digits = "".join(_DIGITS_ONLY_RE.findall(raw))
    if not digits:
        return None
    if len(digits) in (10, 11):
        return f"https://wa.me/55{digits}"
    if len(digits) in (12, 13) and digits.startswith("55"):
        return f"https://wa.me/{digits}"
    return None


def count_email_hits(text: str | None) -> int:
    return len(EMAIL_RE.findall(text or ""))


def count_phone_hits(text: str | None) -> int:
    return len(PHONE_DIGITS_RE.findall(text or ""))
