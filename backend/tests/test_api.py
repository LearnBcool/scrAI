from __future__ import annotations

import json
import time

import pytest
from fastapi.testclient import TestClient

from app.api import deps
from app.core.jobs import JobRegistry
from app.main import app
from app.protocols.crawler import CrawledPage
from app.repositories.lead_repo import LeadRepository
from app.schemas.tools import WebResult
from app.services.outreach_service import OutreachService
from app.services.vector.null_store import NullStore


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
        )


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


def _wait_job(client: TestClient, job_id: str, timeout: float = 10.0) -> dict:
    deadline = time.monotonic() + timeout
    last_status = "queued"
    while time.monotonic() < deadline:
        resp = client.get(f"/api/jobs/{job_id}")
        assert resp.status_code == 200
        data = resp.json()
        last_status = data["status"]
        if last_status in ("completed", "failed", "partial"):
            return data
        time.sleep(0.05)
    pytest.fail(f"Job {job_id} não terminou em {timeout}s (último status: {last_status})")


@pytest.fixture
def client(monkeypatch, db):
    lead_repo = LeadRepository()
    registry = JobRegistry()

    responses = [
        FakeResponse(
            FakeMessage(
                tool_calls=[
                    FakeToolCall(
                        "call-1",
                        "finalize_results",
                        json.dumps(
                            {
                                "summary": "Encontrei 1 lead.",
                                "leads": [
                                    {
                                        "name": "Acme",
                                        "source_url": "https://acme.com",
                                        "emails": ["contato@acme.com"],
                                        "confidence": 0.9,
                                    }
                                ],
                            }
                        ),
                    )
                ]
            )
        ),
        FakeResponse(FakeMessage(content="Prospecção concluída.")),
    ]

    async def fake_llm(messages, tools):
        return responses.pop(0)

    monkeypatch.setattr("app.core.llm.completion_with_tools", fake_llm)

    app.dependency_overrides[deps.get_lead_repo] = lambda: lead_repo
    app.dependency_overrides[deps.get_job_registry] = lambda: registry
    app.dependency_overrides[deps.get_search_provider] = lambda: FakeSearchProvider()
    app.dependency_overrides[deps.get_crawler] = lambda: FakeCrawler()
    app.dependency_overrides[deps.get_vector_store] = lambda: NullStore()
    app.dependency_overrides[deps.get_outreach_service] = lambda: OutreachService(
        lead_repo=lead_repo
    )

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_full_search_leads_outreach_flow(client):
    resp = client.post(
        "/api/search",
        json={"query": "pizzaria em são paulo", "max_leads": 5},
    )
    assert resp.status_code == 202
    body = resp.json()
    job_id = body["job_id"]
    assert body["status_url"] == f"/api/jobs/{job_id}"

    job = _wait_job(client, job_id)
    assert job["status"] == "completed"
    assert job["lead_count"] == 1

    leads_resp = client.get(f"/api/leads?job_id={job_id}")
    assert leads_resp.status_code == 200
    leads_data = leads_resp.json()
    assert leads_data["total"] == 1
    assert leads_data["query"] == "pizzaria em são paulo"
    lead = leads_data["leads"][0]
    assert lead["name"] == "Acme"
    assert "contato@acme.com" in lead["emails"]

    # individual lead lookup
    detail = client.get(f"/api/leads/{lead['id']}")
    assert detail.status_code == 200
    assert detail.json()["name"] == "Acme"

    # outreach choose
    choose = client.post(
        "/api/outreach/choose",
        json={"job_id": job_id, "channel": "email", "lead_ids": [lead["id"]]},
    )
    assert choose.status_code == 200
    plan = choose.json()["plan"]
    assert plan["status"] == "draft"
    assert len(plan["recipients"]) == 1
    assert plan["recipients"][0]["lead_id"] == lead["id"]
    assert plan["recipients"][0]["contact"] == "contato@acme.com"
    assert "{name}" not in plan["recipients"][0]["message"]

    # outreach send (stub)
    send = client.post("/api/outreach/send", json={"plan_id": plan["id"]})
    assert send.status_code == 200
    assert send.json()["delivered"] == 1
    assert send.json()["stub"] is True

    plan_resp = client.get(f"/api/outreach/plans/{plan['id']}")
    assert plan_resp.status_code == 200
    assert plan_resp.json()["status"] == "sent"

    # jobs listing includes our job
    jobs = client.get("/api/jobs").json()
    assert any(j["id"] == job_id for j in jobs)


def test_search_returns_202_immediately_without_llm(client, monkeypatch):
    async def failing_llm(messages, tools):
        raise RuntimeError("LLM não disponível (sem API key)")

    monkeypatch.setattr("app.core.llm.completion_with_tools", failing_llm)

    resp = client.post("/api/search", json={"query": "qualquer negócio"})
    assert resp.status_code == 202
    job_id = resp.json()["job_id"]

    job = _wait_job(client, job_id)
    assert job["status"] == "failed"
    assert "Erro durante a prospecção" in (job.get("error") or "")


def test_job_not_found(client):
    resp = client.get("/api/jobs/nao-existe")
    assert resp.status_code == 404


def test_lead_not_found(client):
    resp = client.get("/api/leads/nao-existe")
    assert resp.status_code == 404
