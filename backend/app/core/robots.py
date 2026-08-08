from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass
from urllib.parse import urlparse

import httpx

from app.utils.text import extract_domain

logger = logging.getLogger(__name__)

_TIMEOUT = httpx.Timeout(10.0)
_CACHE_TTL_S = 3600.0
_MIN_CRAWL_DELAY_S = 1.0


@dataclass
class _RobotsPolicy:
    disallow: tuple[str, ...] | None  # None -> no robots.txt found (allow all)
    crawl_delay: float


_CACHE: dict[str, tuple[float, _RobotsPolicy]] = {}
_LOCK = asyncio.Lock()


async def robots_allows(url: str) -> bool:
    """Best-effort robots.txt check (404 / errors -> allow; fail-open with log)."""
    domain = extract_domain(url)
    if not domain:
        return True
    policy = await _policy_for(domain)
    if policy.disallow is None:
        return True
    path = urlparse(url).path or "/"
    for prefix in policy.disallow:
        if prefix and path.startswith(prefix):
            return False
    return True


async def crawl_delay_for(url_or_domain: str) -> float:
    """Crawl-delay for a domain with a 1.0s floor (best effort, cached)."""
    domain = extract_domain(url_or_domain)
    if not domain:
        return _MIN_CRAWL_DELAY_S
    policy = await _policy_for(domain)
    return max(_MIN_CRAWL_DELAY_S, policy.crawl_delay)


async def _policy_for(domain: str) -> _RobotsPolicy:
    now = time.monotonic()
    cached = _CACHE.get(domain)
    if cached and now - cached[0] < _CACHE_TTL_S:
        return cached[1]
    policy = await _fetch_policy(domain)
    _CACHE[domain] = (time.monotonic(), policy)
    return policy


async def _fetch_policy(domain: str) -> _RobotsPolicy:
    try:
        async with _LOCK:
            cached = _CACHE.get(domain)
            if cached and time.monotonic() - cached[0] < _CACHE_TTL_S:
                return cached[1]
            async with httpx.AsyncClient(timeout=_TIMEOUT, follow_redirects=True) as client:
                resp = await client.get(f"https://{domain}/robots.txt")
        if resp.status_code in (404, 429) or resp.status_code >= 500:
            return _RobotsPolicy(disallow=None, crawl_delay=_MIN_CRAWL_DELAY_S)
        if resp.status_code != 200:
            return _RobotsPolicy(disallow=None, crawl_delay=_MIN_CRAWL_DELAY_S)
        return _parse_robots(resp.text)
    except Exception as exc:  # noqa: BLE001
        logger.warning("robots.txt check failed for %s (fail-open): %s", domain, exc)
        return _RobotsPolicy(disallow=None, crawl_delay=_MIN_CRAWL_DELAY_S)


def _parse_robots(text: str) -> _RobotsPolicy:
    disallow: list[str] = []
    crawl_delay = _MIN_CRAWL_DELAY_S
    in_agent = False
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        key, _, value = line.partition(":")
        key = key.strip().lower()
        value = value.strip()
        if key == "user-agent":
            in_agent = value.lower() in ("*", "scrapai", "googlebot")
        elif key == "disallow" and in_agent:
            if value:
                disallow.append(value)
        elif key == "crawl-delay":
            try:
                crawl_delay = max(_MIN_CRAWL_DELAY_S, float(value))
            except ValueError:
                continue
    return _RobotsPolicy(disallow=tuple(disallow), crawl_delay=crawl_delay)
