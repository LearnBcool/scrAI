from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable


@dataclass
class CrawledPage:
    url: str
    ok: bool
    title: str | None = None
    text: str = field(default="")
    email_hits: int = 0
    phone_hits: int = 0
    needed_js: bool = False
    error: str | None = None


@runtime_checkable
class CrawlerProvider(Protocol):
    async def crawl(self, url: str, js: bool = False) -> CrawledPage: ...
