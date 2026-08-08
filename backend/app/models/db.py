from __future__ import annotations

import psycopg
from psycopg.rows import dict_row

from app.config import settings


def get_connection() -> psycopg.Connection:
    """PostgreSQL connection via DATABASE_URL with dict-row access (psycopg 3)."""
    if not settings.database_url:
        raise RuntimeError(
            "DATABASE_URL não configurado. Defina DATABASE_URL no ambiente ou "
            "no arquivo .env (ex.: postgresql://user:password@localhost:5432/scrapai)."
        )
    return psycopg.connect(settings.database_url, row_factory=dict_row)


def init_db() -> None:
    """Create the initial tables (idempotent: IF NOT EXISTS)."""
    from app.models.lead import LEAD_DDL
    from app.models.outreach import OUTREACH_PLANS_DDL, OUTREACH_RECIPIENTS_DDL

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            for ddl in (LEAD_DDL, OUTREACH_PLANS_DDL, OUTREACH_RECIPIENTS_DDL):
                for statement in ddl.split(";"):
                    statement = statement.strip()
                    if statement:
                        cur.execute(statement)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
