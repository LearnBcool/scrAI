from __future__ import annotations

import os
import shutil
from collections.abc import Generator
from urllib.parse import urlparse

import pytest

from app.config import settings

# A suíte de testes é DESTRUTIVA (trunca tabelas). Só pode rodar contra uma
# instância PostgreSQL local de teste.
_ALLOWED_TEST_HOSTS = {"localhost", "127.0.0.1", "::1"}


def _validate_test_url(url: str) -> str:
    if not url:
        raise RuntimeError(
            "TEST_DATABASE_URL não definida. Os testes de integração exigem "
            "uma instância PostgreSQL de teste (ex.: "
            "TEST_DATABASE_URL=postgresql://user:pass@localhost:5432/scrapai_test)."
        )
    host = (urlparse(url).hostname or "").lower()
    if host not in _ALLOWED_TEST_HOSTS:
        raise RuntimeError(
            f"Recusando execução de testes: TEST_DATABASE_URL aponta para o "
            f"host '{host}', que não é local. A suíte é destrutiva e só pode "
            f"rodar contra uma instância de teste local (localhost/127.0.0.1)."
        )
    return url


def _find_initdb() -> str | None:
    """Localiza binários initdb (PATH ou binários portáteis de teste)."""
    found = shutil.which("initdb")
    if found:
        return found
    candidates = [os.environ.get("PG_BIN", "")]
    for candidate in candidates:
        if candidate and os.path.isfile(os.path.join(candidate, "initdb")):
            os.environ["PATH"] = candidate + os.pathsep + os.environ["PATH"]
            return os.path.join(candidate, "initdb")
    return None


@pytest.fixture(scope="session")
def test_db_url() -> Generator[str, None, None]:
    """URL de um PostgreSQL real de teste.

    Prioridade:
      1. TEST_DATABASE_URL (com guarda anti-produção);
      2. instância temporária via testing.postgresql (binários portáteis).
    """
    env_url = os.environ.get("TEST_DATABASE_URL") or ""
    if env_url:
        yield _validate_test_url(env_url)
        return

    if _find_initdb() is None:
        raise RuntimeError(
            "TEST_DATABASE_URL não definida e nenhum PostgreSQL local "
            "encontrado (initdb ausente no PATH). Configure TEST_DATABASE_URL "
            "apontando para uma instância PostgreSQL de teste local ou "
            "disponibilize binários de teste via PG_BIN."
        )

    import testing.postgresql

    pg = testing.postgresql.Postgresql()
    try:
        yield pg.url()
    finally:
        pg.stop()


@pytest.fixture
def db(
    test_db_url: str,
    monkeypatch: pytest.MonkeyPatch,
) -> Generator[None, None, None]:
    """Configura o settings para o banco de teste e isola cada teste."""
    monkeypatch.setattr(settings, "database_url", test_db_url)

    from app.models.db import get_connection, init_db

    init_db()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE leads, outreach_plans, outreach_recipients")
        conn.commit()
    finally:
        conn.close()
    yield
