from __future__ import annotations

import asyncio
import logging
import time

from crawl4ai import AsyncWebCrawler, BrowserConfig, CacheMode, CrawlerRunConfig

from app.config import settings
from app.protocols.crawler import CrawledPage
from app.utils.text import extract_domain
from app.utils.validators import count_email_hits, count_phone_hits

logger = logging.getLogger(__name__)

_crawler: AsyncWebCrawler | None = None
_js_crawler: AsyncWebCrawler | None = None
_start_lock = asyncio.Lock()

_last_access: dict[str, float] = {}
_delay_lock = asyncio.Lock()

_MIN_TEXT_LENGTH = 200


def get_shared_crawler() -> AsyncWebCrawler:
    return _get_crawler(js=False)


def _get_crawler(js: bool = False) -> AsyncWebCrawler:
    global _crawler, _js_crawler
    if js:
        if _js_crawler is None:
            _js_crawler = AsyncWebCrawler(config=BrowserConfig(enable_stealth=True))
        return _js_crawler
    if _crawler is None:
        _crawler = AsyncWebCrawler()
    return _crawler


class Crawl4AIService:
    """Shared-lazy crawl4ai crawler with per-domain min delay and JS retry."""

    def __init__(self) -> None:
        self._semaphore = asyncio.Semaphore(max(1, settings.crawl_concurrency))

    async def crawl(self, url: str, js: bool = False) -> CrawledPage:
        domain = extract_domain(url)
        await self._enforce_delay(domain)
        try:
            page = await self._crawl_once(url, js=js)
        except Exception as exc:  # noqa: BLE001
            logger.warning("crawl4ai falhou para %s: %s", url, exc)
            return CrawledPage(url=url, ok=False, error=str(exc))
        if page.ok and len((page.text or "").strip()) < _MIN_TEXT_LENGTH:
            logger.info("Conteúdo curto em %s — nova tentativa com JS.", url)
            try:
                await self._enforce_delay(domain)
                page = await self._crawl_once(url, js=True)
            except Exception as exc:  # noqa: BLE001
                logger.warning("crawl4ai JS retry falhou para %s: %s", url, exc)
        return page

    async def _crawl_once(self, url: str, js: bool) -> CrawledPage:
        crawler = _get_crawler(js=js)
        if not getattr(crawler, "ready", False):
            async with _start_lock:
                if not getattr(crawler, "ready", False):
                    await crawler.start()
        config = CrawlerRunConfig(
            page_timeout=settings.crawl_page_timeout_ms,
            wait_until="domcontentloaded",
            cache_mode=CacheMode.ENABLED,
            delay_before_return_html=min(settings.crawl_domain_delay_s, 3.0),
        )
        async with self._semaphore:
            result = await crawler.arun(url, config=config)
        return _result_to_page(url, result, js=js)

    async def _enforce_delay(self, domain: str | None) -> None:
        if not domain:
            return
        delay = max(float(settings.crawl_domain_delay_s), 1.0)
        async with _delay_lock:
            now = time.monotonic()
            last = _last_access.get(domain, 0.0)
            wait = delay - (now - last)
            if wait > 0:
                await asyncio.sleep(wait)
            _last_access[domain] = time.monotonic()


def _result_to_page(url: str, result: object, js: bool) -> CrawledPage:
    ok = bool(getattr(result, "success", False))
    error = getattr(result, "error_message", None)
    text = getattr(result, "markdown", None) or ""
    if not text:
        cleaned = getattr(result, "cleaned_html", None) or ""
        text = cleaned or ""
    title = getattr(result, "title", None) or None
    return CrawledPage(
        url=url,
        ok=ok,
        title=title,
        text=str(text),
        email_hits=count_email_hits(text),
        phone_hits=count_phone_hits(text),
        needed_js=js,
        error=error,
    )
