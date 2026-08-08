from __future__ import annotations

import json

from app.schemas.lead import Lead

LEAD_DDL = """
CREATE TABLE IF NOT EXISTS leads (
    id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL,
    name TEXT NOT NULL,
    segment TEXT,
    city TEXT,
    state TEXT,
    website TEXT,
    emails TEXT NOT NULL DEFAULT '[]',
    phones TEXT NOT NULL DEFAULT '[]',
    whatsapp TEXT NOT NULL DEFAULT '[]',
    social TEXT NOT NULL DEFAULT '{}',
    confidence REAL NOT NULL DEFAULT 0,
    source_url TEXT,
    notes TEXT,
    created_at TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'new'
);
CREATE INDEX IF NOT EXISTS idx_leads_job_id ON leads(job_id);
CREATE INDEX IF NOT EXISTS idx_leads_segment ON leads(segment);
CREATE INDEX IF NOT EXISTS idx_leads_city ON leads(city);
"""

LEAD_COLUMNS = (
    "id",
    "job_id",
    "name",
    "segment",
    "city",
    "state",
    "website",
    "emails",
    "phones",
    "whatsapp",
    "social",
    "confidence",
    "source_url",
    "notes",
    "created_at",
    "status",
)


def lead_to_row(lead: Lead) -> dict:
    return {
        "id": lead.id,
        "job_id": lead.job_id,
        "name": lead.name,
        "segment": lead.segment,
        "city": lead.city,
        "state": lead.state,
        "website": lead.website,
        "emails": json.dumps(lead.emails, ensure_ascii=False),
        "phones": json.dumps(lead.phones, ensure_ascii=False),
        "whatsapp": json.dumps(lead.whatsapp, ensure_ascii=False),
        "social": json.dumps(lead.social, ensure_ascii=False),
        "confidence": lead.confidence,
        "source_url": lead.source_url,
        "notes": lead.notes,
        "created_at": lead.created_at.isoformat(),
        "status": lead.status,
    }


def row_to_lead(row: dict) -> Lead:
    return Lead(
        id=row["id"],
        job_id=row["job_id"],
        name=row["name"],
        segment=row["segment"],
        city=row["city"],
        state=row["state"],
        website=row["website"],
        emails=json.loads(row["emails"] or "[]"),
        phones=json.loads(row["phones"] or "[]"),
        whatsapp=json.loads(row["whatsapp"] or "[]"),
        social=json.loads(row["social"] or "{}"),
        confidence=float(row["confidence"] or 0),
        source_url=row["source_url"] or "",
        notes=row["notes"],
        created_at=row["created_at"],
        status=row["status"],
    )
