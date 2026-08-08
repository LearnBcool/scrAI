from __future__ import annotations

import logging

from playwright.async_api import async_playwright

from app.protocols.crawler import CrawledPage
from app.utils.validators import count_email_hits, count_phone_hits

logger = logging.getLogger(__name__)


class PlaywrightFallbackCrawler:
    """Raw Playwright path used when crawl4ai raises or js=True is requested."""

    async def crawl(self, url: str, js: bool = False) -> CrawledPage:
        text = ""
        title: str | None = None
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                try:
                    page = await browser.new_page()
                    await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    if js:
                        await page.wait_for_timeout(1500)
                    title = await page.title()
                    text = await page.inner_text("body")
                finally:
                    await browser.close()
            ok = bool(text and text.strip())
            return CrawledPage(
                url=url,
                ok=ok,
                title=title,
                text=text,
                email_hits=count_email_hits(text),
                phone_hits=count_phone_hits(text),
                needed_js=js,
                error=None if ok else "Página vazia",
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("Playwright fallback falhou para %s: %s", url, exc)
            return CrawledPage(url=url, ok=False, title=title, text=text, error=str(exc))
