from __future__ import annotations

from app.schemas.outreach import OutreachPlan, OutreachRecipient

OUTREACH_PLANS_DDL = """
CREATE TABLE IF NOT EXISTS outreach_plans (
    id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL,
    channel TEXT NOT NULL,
    message_template TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft',
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_outreach_job_id ON outreach_plans(job_id);
"""

OUTREACH_RECIPIENTS_DDL = """
CREATE TABLE IF NOT EXISTS outreach_recipients (
    id TEXT PRIMARY KEY,
    plan_id TEXT NOT NULL,
    lead_id TEXT NOT NULL,
    name TEXT NOT NULL,
    contact TEXT NOT NULL,
    message TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_recipients_plan ON outreach_recipients(plan_id);
"""


def plan_to_row(plan: OutreachPlan) -> dict:
    return {
        "id": plan.id,
        "job_id": plan.job_id,
        "channel": plan.channel,
        "message_template": plan.message_template,
        "status": plan.status,
        "created_at": plan.created_at.isoformat(),
    }


def row_to_plan(row: dict) -> OutreachPlan:
    return OutreachPlan(
        id=row["id"],
        job_id=row["job_id"],
        channel=row["channel"],
        message_template=row["message_template"],
        status=row["status"],
        created_at=row["created_at"],
    )


def recipient_to_row(plan_id: str, recipient: OutreachRecipient, recipient_id: str) -> dict:
    return {
        "id": recipient_id,
        "plan_id": plan_id,
        "lead_id": recipient.lead_id,
        "name": recipient.name,
        "contact": recipient.contact,
        "message": recipient.message,
    }


def row_to_recipient(row: dict) -> OutreachRecipient:
    return OutreachRecipient(
        lead_id=row["lead_id"],
        name=row["name"],
        contact=row["contact"],
        message=row["message"],
    )
