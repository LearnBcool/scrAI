from __future__ import annotations

from app.models.db import get_connection
from app.models.lead import LEAD_COLUMNS, lead_to_row, row_to_lead
from app.schemas.lead import Lead

_COLUMNS_SQL = ", ".join(LEAD_COLUMNS)
_PLACEHOLDERS_SQL = ", ".join(["%s"] * len(LEAD_COLUMNS))
# UPSERT: preserve `id` as primary key; update all non-key columns on conflict.
_UPDATE_COLUMNS = [col for col in LEAD_COLUMNS if col != "id"]
_UPDATE_SQL = ", ".join(f"{col} = EXCLUDED.{col}" for col in _UPDATE_COLUMNS)
_UPSERT_SQL = (
    f"INSERT INTO leads ({_COLUMNS_SQL}) VALUES ({_PLACEHOLDERS_SQL}) "
    f"ON CONFLICT (id) DO UPDATE SET {_UPDATE_SQL}"
)


class LeadRepository:
    """PostgreSQL-backed storage for leads (psycopg 3)."""

    def bulk_create(self, leads: list[Lead]) -> int:
        if not leads:
            return 0
        rows = [lead_to_row(lead) for lead in leads]
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.executemany(
                    _UPSERT_SQL,
                    [tuple(row[k] for k in LEAD_COLUMNS) for row in rows],
                )
            conn.commit()
            return len(rows)
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def list_by_job(self, job_id: str) -> list[Lead]:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM leads WHERE job_id = %s "
                    "ORDER BY confidence DESC, created_at DESC",
                    (job_id,),
                )
                rows = cur.fetchall()
            return [row_to_lead(row) for row in rows]
        finally:
            conn.close()

    def get_by_id(self, lead_id: str) -> Lead | None:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM leads WHERE id = %s", (lead_id,))
                row = cur.fetchone()
            return row_to_lead(row) if row is not None else None
        finally:
            conn.close()

    def count_by_job(self, job_id: str) -> int:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT COUNT(*) AS n FROM leads WHERE job_id = %s", (job_id,)
                )
                row = cur.fetchone()
            return int(row["n"]) if row else 0
        finally:
            conn.close()

    def list(
        self,
        *,
        job_id: str | None = None,
        segment: str | None = None,
        city: str | None = None,
        q: str | None = None,
    ) -> list[Lead]:
        clauses: list[str] = []
        params: list[object] = []
        if job_id:
            clauses.append("job_id = %s")
            params.append(job_id)
        if segment:
            clauses.append("segment = %s")
            params.append(segment)
        if city:
            clauses.append("city = %s")
            params.append(city)
        if q:
            clauses.append("(name LIKE %s OR website LIKE %s OR source_url LIKE %s)")
            like = f"%{q}%"
            params.extend([like, like, like])
        where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
        sql = f"SELECT * FROM leads{where} ORDER BY confidence DESC, created_at DESC"
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                rows = cur.fetchall()
            return [row_to_lead(row) for row in rows]
        finally:
            conn.close()
