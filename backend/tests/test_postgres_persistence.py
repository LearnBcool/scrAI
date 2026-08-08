from __future__ import annotations

from fastapi.testclient import TestClient

from app.models.db import get_connection
from app.repositories.lead_repo import LeadRepository
from app.schemas.lead import Lead
from app.services.outreach_service import OutreachService


def _make_lead(
    job_id: str,
    name: str,
    *,
    lead_id: str | None = None,
    segment: str | None = None,
    city: str | None = None,
    state: str | None = None,
    website: str | None = None,
    emails: list[str] | None = None,
    phones: list[str] | None = None,
) -> Lead:
    slug = name.lower().replace(" ", "-")
    return Lead(
        id=lead_id or f"lead-{slug}",
        job_id=job_id,
        name=name,
        segment=segment,
        city=city,
        state=state,
        website=website or f"https://{slug}.com.br",
        emails=emails or [f"contato@{slug}.com.br"],
        phones=phones or [],
        source_url=f"https://{slug}.com.br",
    )


def _table_names() -> set[str]:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT tablename FROM pg_tables "
                "WHERE schemaname = 'public' "
                "AND tablename IN ('leads', 'outreach_plans', 'outreach_recipients')"
            )
            return {row["tablename"] for row in cur.fetchall()}
    finally:
        conn.close()


# ---- 1. init_db cria tabelas -------------------------------------------


def test_init_db_creates_tables(db):
    assert {"leads", "outreach_plans", "outreach_recipients"} <= _table_names()


# ---- 2/3. LeadRepository.bulk_create + UPSERT --------------------------


def test_bulk_create_creates_lead(db):
    repo = LeadRepository()
    lead = _make_lead("job-1", "Acme")

    created = repo.bulk_create([lead])

    assert created == 1
    assert repo.count_by_job("job-1") == 1
    stored = repo.get_by_id(lead.id)
    assert stored is not None
    assert stored.name == "Acme"
    assert stored.emails == ["contato@acme.com.br"]


def test_bulk_create_with_same_id_updates_lead(db):
    repo = LeadRepository()
    original = _make_lead("job-1", "Acme", lead_id="lead-acme", emails=["velho@acme.com.br"])
    updated = _make_lead("job-1", "Acme Renovada", lead_id="lead-acme", emails=["novo@acme.com.br"])

    repo.bulk_create([original])
    repo.bulk_create([updated])

    assert repo.count_by_job("job-1") == 1  # mesmo id: não duplica
    stored = repo.get_by_id("lead-acme")
    assert stored is not None
    assert stored.name == "Acme Renovada"
    assert stored.emails == ["novo@acme.com.br"]


# ---- 4/5/6. list_by_job / get_by_id / count_by_job ---------------------


def test_list_by_job_returns_only_leads_of_job(db):
    repo = LeadRepository()
    repo.bulk_create(
        [
            _make_lead("job-1", "Acme"),
            _make_lead("job-1", "Brasil Ltda"),
            _make_lead("job-2", "Outra Empresa"),
        ]
    )

    leads = repo.list_by_job("job-1")

    assert {lead.name for lead in leads} == {"Acme", "Brasil Ltda"}


def test_get_by_id_returns_lead_or_none(db):
    repo = LeadRepository()
    lead = _make_lead("job-1", "Acme")

    repo.bulk_create([lead])

    assert repo.get_by_id(lead.id) is not None
    assert repo.get_by_id("nao-existe") is None


def test_count_by_job_counts_leads(db):
    repo = LeadRepository()
    repo.bulk_create(
        [
            _make_lead("job-1", "Acme"),
            _make_lead("job-1", "Brasil Ltda"),
            _make_lead("job-2", "Outra"),
        ]
    )

    assert repo.count_by_job("job-1") == 2
    assert repo.count_by_job("job-vazio") == 0


# ---- 7. filtros de list ------------------------------------------------


def test_list_filters_by_segment_city_and_q(db):
    repo = LeadRepository()
    repo.bulk_create(
        [
            _make_lead("job-1", "Pizzaria Bella", segment="restaurante", city="curitiba"),
            _make_lead("job-1", "Advogado Silva", segment="juridico", city="curitiba"),
            _make_lead("job-1", "Loja Moda", segment="vestuario", city="florianopolis"),
        ]
    )

    assert {l.name for l in repo.list(job_id="job-1", segment="juridico")} == {"Advogado Silva"}
    assert {l.name for l in repo.list(job_id="job-1", city="curitiba")} == {
        "Pizzaria Bella",
        "Advogado Silva",
    }
    assert {l.name for l in repo.list(job_id="job-1", q="bella")} == {"Pizzaria Bella"}
    # q busca name/website/source_url (não city)
    assert {l.name for l in repo.list(job_id="job-1", q="loja-moda")} == {"Loja Moda"}


# ---- 8/9/10. Outreach: salvar / carregar / send ------------------------


def _build_plan_with_lead() -> tuple[OutreachService, str, str]:
    repo = LeadRepository()
    lead = _make_lead("job-1", "Acme", emails=["contato@acme.com.br"])
    repo.bulk_create([lead])
    service = OutreachService(lead_repo=repo)
    plan = service.build_plan(
        job_id="job-1",
        channel="email",
        lead_ids=[lead.id],
    )
    return service, plan.id, lead.id


def test_outreach_plan_can_be_saved(db):
    service, plan_id, _ = _build_plan_with_lead()

    plan = service.load_plan(plan_id)

    assert plan is not None
    assert plan.channel == "email"
    assert len(plan.recipients) == 1


def test_outreach_plan_can_be_loaded_with_recipients(db):
    service, plan_id, lead_id = _build_plan_with_lead()

    plan = service.load_plan(plan_id)

    assert plan is not None
    assert plan.recipients[0].lead_id == lead_id
    assert plan.recipients[0].contact == "contato@acme.com.br"
    assert "{name}" not in plan.recipients[0].message
    assert "Acme" in plan.recipients[0].message


def test_outreach_send_changes_status_to_sent(db):
    service, plan_id, _ = _build_plan_with_lead()

    result = service.send(plan_id)

    assert result.stub is True
    assert result.delivered == 1
    plan = service.load_plan(plan_id)
    assert plan is not None
    assert plan.status == "sent"


# ---- 11/12. API continua inicializando e raiz responde ok ---------------


def test_api_initializes_with_postgresql(db):
    from app.main import app

    with TestClient(app) as client:
        resp = client.get("/")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"
        assert resp.json()["app"] == "scrapAI"


def test_root_endpoint_returns_status_ok(db):
    from app.main import app

    with TestClient(app) as client:
        resp = client.get("/")

    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
