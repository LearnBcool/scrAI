from __future__ import annotations

from app.config import settings
from app.protocols.search import SearchProvider
from app.services.search.ddg import DDGSearchProvider
from app.services.search.serpapi import SerpAPISearchProvider
from app.services.search.tavily import TavilySearchProvider


def get_search_provider() -> SearchProvider:
    name = (settings.search_provider or "duckduckgo").strip().lower()
    if name == "duckduckgo":
        return DDGSearchProvider()
    if name == "tavily":
        if not settings.tavily_api_key:
            raise RuntimeError(
                "Provedor de busca 'tavily' selecionado, mas TAVILY_API_KEY não está configurada."
            )
        return TavilySearchProvider(settings.tavily_api_key)
    if name == "serpapi":
        if not settings.serpapi_api_key:
            raise RuntimeError(
                "Provedor de busca 'serpapi' selecionado, mas SERPAPI_API_KEY não está configurada."
            )
        return SerpAPISearchProvider(settings.serpapi_api_key)
    raise RuntimeError(
        f"Provedor de busca desconhecido: '{settings.search_provider}'. "
        "Use 'duckduckgo', 'tavily' ou 'serpapi'."
    )
