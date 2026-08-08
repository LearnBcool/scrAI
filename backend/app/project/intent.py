from __future__ import annotations

import re
from dataclasses import dataclass

from app.config import settings
from app.schemas.search import SearchRequest

UF_LIST = {
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA",
    "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN",
    "RS", "RO", "RR", "SC", "SP", "SE", "TO",
}

STOPWORDS = {
    "de", "da", "do", "das", "dos", "em", "no", "na", "nos", "nas",
    "para", "por", "com", "e", "ou", "que", "uma", "um", "o", "a",
    "os", "as", "ao", "aos", "empresa", "empresas", "fabricante",
    "fabricantes", "loja", "lojas", "quero", "buscar", "encontrar",
}

SEGMENT_HINTS = [
    "pizzaria", "restaurante", "hamburgueria", "sorveteria", "cafeteria",
    "padaria", "academia", "escola", "clínica", "consultório", "advocacia",
    "contabilidade", "imobiliária", "construtora", "marcenaria", "mecânica",
    "salão de beleza", "barbearia", "pet shop", "farmácia", "supermercado",
    "mercearia", "transportadora", "agência", "hotel", "pousada", "oficina",
]


@dataclass
class IntentHints:
    segment: str | None = None
    city: str | None = None
    state: str | None = None


def strip_stopwords(text: str) -> str:
    tokens = re.findall(r"[\wÀ-ÿ'-]+", text or "", re.UNICODE)
    kept = [token for token in tokens if token.lower() not in STOPWORDS]
    return " ".join(kept)


def extract_hints(text: str) -> IntentHints:
    """Best-effort extraction of segment/city/state hints from free text."""
    cleaned = text or ""
    state: str | None = None
    for token in re.findall(r"\b([A-Z]{2})\b", cleaned):
        if token in UF_LIST:
            state = token
            break

    city: str | None = None
    match = re.search(
        r"(?:em|de|na cidade de|na|no município de)\s+([A-ZÀ-Ú][\wÀ-ú.'-]*(?:\s+[A-ZÀ-Ú][\wÀ-ú.'-]*){0,3})",
        cleaned,
    )
    if match:
        candidate = match.group(1).strip().rstrip(".,")
        if len(candidate) <= 40:
            city = candidate

    segment: str | None = None
    lowered = cleaned.lower()
    for keyword in SEGMENT_HINTS:
        if keyword in lowered:
            segment = keyword
            break

    return IntentHints(segment=segment, city=city, state=state)


def build_user_prompt(request: SearchRequest) -> str:
    parts = [
        f"Busque e colete até {request.max_leads} leads de empresas relacionadas a: "
        f"{request.query or 'prospecção geral'}."
    ]
    if request.segment:
        parts.append(f"Segmento: {request.segment}.")
    if request.city:
        parts.append(f"Cidade: {request.city}.")
    if request.state:
        parts.append(f"Estado (UF): {request.state}.")
    page_limit = min(request.max_pages or settings.crawl_max_pages, settings.crawl_max_pages)
    parts.append(f"Limite de páginas a visitar: {page_limit}.")
    parts.append(
        "Ao final, chame finalize_results com TODOS os leads encontrados e um resumo em português (PT-BR)."
    )
    return "\n".join(parts)
