from __future__ import annotations

import re

from app.schemas.lead import ContactInfo
from app.utils.text import extract_domain, normalize_url
from app.utils.validators import build_wa_link, normalize_email, normalize_phone

PLAIN_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
MAILTO_RE = re.compile(r"mailto:([^\"'\s<>]+)")

BR_PHONE_RE = re.compile(r"\(\s*(\d{2})\s*\)\s*(\d{4,5})\s*[-.\s]?\s*(\d{4})")
PHONE_DIGITS_RE = re.compile(r"\d{10,13}")

URL_RE = re.compile(r"https?://[^\s<>\"'()]+")
WA_LINK_RE = re.compile(r"(?:wa\.me|api\.whatsapp\.com)[^\s\"'<>]*")
WA_PHONE_PARAM_RE = re.compile(r"(?:wa\.me/|phone=)(\d+)")

INSTAGRAM_RE = re.compile(
    r"https?://(?:www\.)?instagram\.com/([A-Za-z0-9_.]+)"
)
LINKEDIN_RE = re.compile(
    r"https?://(?:www\.)?linkedin\.com/((?:in|company|school)/[A-Za-z0-9_.\-%]+)"
)
FACEBOOK_RE = re.compile(
    r"https?://(?:www\.|m\.)?facebook\.com/([A-Za-z0-9_.\-]+)"
)
HANDLE_RE = re.compile(r"(?<![A-Za-z0-9_.])@([A-Za-z0-9_.]{2,30})(?![A-Za-z0-9_.])")

_SOCIAL_DOMAINS = {
    "instagram.com",
    "linkedin.com",
    "facebook.com",
    "twitter.com",
    "x.com",
    "wa.me",
    "wa.link",
    "whatsapp.com",
    "api.whatsapp.com",
    "t.me",
}


def extract_contacts(text: str | None, html: str | None = None) -> ContactInfo:
    combined = text or ""
    if html:
        combined = f"{combined}\n{html}"

    emails = extract_emails(combined)
    phones = extract_phones(combined)
    whatsapp = extract_whatsapp(combined)
    instagram = extract_instagram(combined)
    linkedin = extract_linkedin(combined)
    facebook = extract_facebook(combined)
    if instagram is None:
        handles = HANDLE_RE.findall(combined)
        if handles:
            instagram = f"https://instagram.com/{handles[0].lower()}"
    website = extract_website(combined)

    return ContactInfo(
        emails=emails,
        phones=phones,
        whatsapp=whatsapp,
        instagram=instagram,
        linkedin=linkedin,
        facebook=facebook,
        website=website,
    )


def extract_emails(text: str) -> list[str]:
    emails: list[str] = []
    for match in PLAIN_EMAIL_RE.findall(text):
        norm = normalize_email(match)
        if norm and norm not in emails:
            emails.append(norm)
    for match in MAILTO_RE.findall(text):
        norm = normalize_email(match)
        if norm and norm not in emails:
            emails.append(norm)
    return emails


def extract_phones(text: str) -> list[str]:
    wa_digits = {m for m in re.findall(r"(?:wa\.me/|phone=)(\d+)", text)}
    phones: list[str] = []

    for a, b, c in BR_PHONE_RE.findall(text):
        raw = f"{a}{b}{c}"
        if raw in wa_digits:
            continue
        norm = normalize_phone(raw)
        if norm and norm not in phones:
            phones.append(norm)

    for raw in PHONE_DIGITS_RE.findall(text):
        if raw in wa_digits:
            continue
        norm = normalize_phone(raw)
        if norm and norm not in phones:
            phones.append(norm)
    return phones


def extract_whatsapp(text: str) -> list[str]:
    whats: list[str] = []
    for link in WA_LINK_RE.findall(text):
        match = WA_PHONE_PARAM_RE.search(link)
        if not match:
            continue
        wa_link = build_wa_link(match.group(1))
        if wa_link and wa_link not in whats:
            whats.append(wa_link)
    return whats


def extract_instagram(text: str) -> str | None:
    match = INSTAGRAM_RE.search(text)
    if match:
        return f"https://instagram.com/{match.group(1)}"
    return None


def extract_linkedin(text: str) -> str | None:
    match = LINKEDIN_RE.search(text)
    if match:
        return f"https://linkedin.com/{match.group(1)}"
    return None


def extract_facebook(text: str) -> str | None:
    match = FACEBOOK_RE.search(text)
    if match:
        return f"https://facebook.com/{match.group(1)}"
    return None


def extract_website(text: str) -> str | None:
    for raw in URL_RE.findall(text):
        cleaned = raw.rstrip(".,;:!?)\"']")
        domain = extract_domain(cleaned)
        if not domain:
            continue
        if domain in _SOCIAL_DOMAINS:
            continue
        return normalize_url(cleaned)
    return None
