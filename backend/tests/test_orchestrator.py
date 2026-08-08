from __future__ import annotations

import asyncio
import json

import pytest

from app.agents.orchestrator import SearchOrchestrator
from app.config import settings
from app.protocols.crawler import CrawledPage
from app.repositories.lead_repo import LeadRepository
from app.schemas.search import SearchRequest
from app.schemas.tools import FinalizeOutput, WebResult
from app.services.lead_service import LeadService
from app.services.vector.null_store import NullStore


# ---- fakes -------------------------------------------------------------

class FakeFunction:
    def __init__(self, name: str, arguments: str):
        self.name = name
        self.arguments = arguments


class FakeToolCall:
    def __init__(self, tool_id: str, name: str, arguments: str):
        self.id = tool_id
        self.function = FakeFunction(name, arguments)


class FakeMessage:
    def __init__(self, content: str | None = None, tool_calls: list[FakeToolCall] | None = None):
        self.content = content
        self.tool_calls = tool_calls or []


class FakeChoice:
    def __init__(self, message: FakeMessage):
        self.message = message


class FakeResponse:
    def __init__(self, message: FakeMessage):
        self.choices = [FakeChoice(message)]


class FakeSearchProvider:
    async def search(self, query: str, max_results: int) -> list[WebResult]:
        return [
            WebResult(url="https://acme.com", title="Acme", snippet="Pizzaria", rank=1)
        ]


class FakeCrawler:
    async def crawl(self, url: str, js: bool = False) -> CrawledPage:
        return CrawledPage(
            url=url,
            ok=True,
            title="Acme Pizzaria",
            text="contato@acme.com (11) 91234-5678 https://wa.me/5511912345678",
            needed_js=js,
        )


LEAD = {
    "name": "Acme",
    "source_url": "https://acme.com",
    "emails": ["contato@acme.com"],
    "confidence": 0.9,
}

REQUEST = SearchRequest(query="pizzaria em são paulo", max_leads=3)


def make_orchestrator() -> SearchOrchestrator:
    lead_repo = LeadRepository()
    return SearchOrchestrator(
        job_id="job-test",
        search_provider=FakeSearchProvider(),
        crawler=FakeCrawler(),
        lead_service=LeadService(lead_repo=lead_repo),
    )


def finalize_response(summary: str, leads: list[dict]) -> FakeResponse:
    return FakeResponse(
        FakeMessage(
            tool_calls=[
                FakeToolCall(
                    "call-finalize",
                    "finalize_results",
                    json.dumps({"summary": summary, "leads": leads}),
                )
            ]
        )
    )


# ---- tests -------------------------------------------------------------


def test_orchestrator_ends_on_finalize_results(monkeypatch, db):
    responses = [
        finalize_response("Encontrei 1 lead.", [LEAD]),
        FakeResponse(FakeMessage(content="Prospecção concluída.")),
    ]

    async def fake_completion(messages, tools):
        return responses.pop(0)

    monkeypatch.setattr("app.core.llm.completion_with_tools", fake_completion)

    result = asyncio.run(make_orchestrator().run(REQUEST, on_stage=None))

    assert isinstance(result, FinalizeOutput)
    assert result.ok is True
    assert result.accepted == 1
    assert result.rejected == 0


def test_orchestrator_max_steps_guard_auto_finalizes(monkeypatch, db):
    monkeypatch.setattr(settings, "max_tool_steps", 3)
    call_count = {"n": 0}

    async def fake_completion(messages, tools):
        call_count["n"] += 1
        return FakeResponse(
            FakeMessage(
                tool_calls=[
                    FakeToolCall(
                        "call-search",
                        "search_web",
                        json.dumps({"query": "pizzaria", "max_results": 3}),
                    )
                ]
            )
        )

    monkeypatch.setattr("app.core.llm.completion_with_tools", fake_completion)

    result = asyncio.run(make_orchestrator().run(REQUEST, on_stage=None))

    assert call_count["n"] == 3  # step cap reached
    assert isinstance(result, FinalizeOutput)
    assert result.accepted == 0  # no extract -> no leads -> auto-finalize


def test_orchestrator_malformed_args_fed_back(monkeypatch, db):
    seen: list[list[dict]] = []
    responses = [
        FakeResponse(
            FakeMessage(tool_calls=[FakeToolCall("c1", "finalize_results", "not-json{{{")])
        ),
        finalize_response("ok", [LEAD]),
        FakeResponse(FakeMessage(content="fim")),
    ]

    async def fake_completion(messages, tools):
        seen.append(list(messages))
        return responses.pop(0)

    monkeypatch.setattr("app.core.llm.completion_with_tools", fake_completion)

    result = asyncio.run(make_orchestrator().run(REQUEST, on_stage=None))

    assert result.ok is True
    assert result.accepted == 1
    assert any(
        "argumentos JSON inválidos" in str(message.get("content"))
        for message in seen[1]
    )


def test_orchestrator_unknown_tool_fed_back(monkeypatch, db):
    seen: list[list[dict]] = []
    responses = [
        FakeResponse(
            FakeMessage(tool_calls=[FakeToolCall("c1", "bogus_tool", "{}")])
        ),
        finalize_response("ok", [LEAD]),
        FakeResponse(FakeMessage(content="fim")),
    ]

    async def fake_completion(messages, tools):
        seen.append(list(messages))
        return responses.pop(0)

    monkeypatch.setattr("app.core.llm.completion_with_tools", fake_completion)

    result = asyncio.run(make_orchestrator().run(REQUEST, on_stage=None))

    assert result.ok is True
    assert result.accepted == 1
    assert any(
        "Erro ao executar 'bogus_tool'" in str(message.get("content"))
        for message in seen[1]
    )


def test_orchestrator_llm_failure_propagates(monkeypatch, db):
    async def failing_completion(messages, tools):
        raise RuntimeError("falha simulada do LLM")

    monkeypatch.setattr("app.core.llm.completion_with_tools", failing_completion)

    with pytest.raises(RuntimeError, match="falha simulada"):
        asyncio.run(make_orchestrator().run(REQUEST, on_stage=None))
