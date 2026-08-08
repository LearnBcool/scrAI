from __future__ import annotations

import logging

from app.protocols.crawler import CrawledPage, CrawlerProvider
from app.services.crawler.crawl4ai_service import Crawl4AIService
from app.services.crawler.playwright_fallback import PlaywrightFallbackCrawler

logger = logging.getLogger(__name__)


class CompositeCrawler:
    """Crawl4AI first; Playwright fallback on crawl4ai error or when js=True."""

    def __init__(self) -> None:
        self._crawl4ai = Crawl4AIService()
        self._playwright = PlaywrightFallbackCrawler()

    async def crawl(self, url: str, js: bool = False) -> CrawledPage:
        if js:
            page = await self._playwright.crawl(url, js=True)
            if page.ok:
                return page
        page = await self._crawl4ai.crawl(url, js=js)
        if page.ok:
            return page
        logger.info("Fallback para Playwright em %s (crawl4ai: %s)", url, page.error)
        return await self._playwright.crawl(url, js=js)


_crawler: CompositeCrawler | None = None


def get_crawler() -> CrawlerProvider:
    global _crawler
    if _crawler is None:
        _crawler = CompositeCrawler()
    return _crawler
