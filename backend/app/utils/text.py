from __future__ import annotations

import re
from urllib.parse import urlparse

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


def normalize_url(url: str | None) -> str | None:
    """Ensure scheme and return a usable absolute URL, or None."""
    if not url:
        return None
    url = url.strip()
    if not url:
        return None
    if "://" not in url:
        url = f"https://{url}"
    try:
        parsed = urlparse(url)
        if not parsed.netloc:
            return None
    except ValueError:
        return None
    return url


def extract_domain(url: str | None) -> str | None:
    """Return the lowercase netloc (without leading 'www.') of a URL, or None."""
    if not url:
        return None
    value = url.strip()
    if "://" not in value:
        value = f"https://{value}"
    try:
        netloc = urlparse(value).netloc.lower()
    except ValueError:
        return None
    if not netloc:
        return None
    if netloc.startswith("www."):
        netloc = netloc[4:]
    return netloc


def html_to_text(html: str | None, max_chars: int = 2000) -> str:
    """Crude html -> text snippet (tags stripped, whitespace collapsed)."""
    text = _TAG_RE.sub(" ", html or "")
    text = _WS_RE.sub(" ", text).strip()
    return text[:max_chars]
