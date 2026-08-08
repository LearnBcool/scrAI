from __future__ import annotations

import uuid

from app.models.db import get_connection
from app.models.outreach import (
    plan_to_row,
    recipient_to_row,
    row_to_plan,
    row_to_recipient,
)
from app.project.outreach import (
    default_template_for,
    render_template,
    validate_channel,
)
from app.repositories.lead_repo import LeadRepository
from app.schemas.lead import Lead
from app.schemas.outreach import (
    OutreachPlan,
    OutreachRecipient,
    OutreachSendResult,
)
from app.utils.validators import build_wa_link, normalize_email


class OutreachService:
    """Builds outreach plans and performs stub sends."""

    def __init__(self, lead_repo: LeadRepository) -> None:
        self._lead_repo = lead_repo

    def build_plan(
        self,
        job_id: str,
        channel: str,
        lead_ids: list[str],
        template: str | None = None,
    ) -> OutreachPlan:
        channel = validate_channel(channel)
        resolved_template = template or default_template_for(channel)
        recipients: list[OutreachRecipient] = []
        for lead_id in lead_ids:
            lead = self._lead_repo.get_by_id(lead_id)
            if lead is None:
                continue
            contact = pick_contact(lead, channel)
            if not contact:
                continue
            recipients.append(
                OutreachRecipient(
                    lead_id=lead.id,
                    name=lead.name,
                    contact=contact,
                    message=render_template(resolved_template, lead),
                )
            )
        plan = OutreachPlan(
            job_id=job_id,
            channel=channel,
            recipients=recipients,
            message_template=resolved_template,
        )
        self._save_plan(plan)
        return plan

    def load_plan(self, plan_id: str) -> OutreachPlan | None:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM outreach_plans WHERE id = %s", (plan_id,)
                )
                row = cur.fetchone()
                if row is None:
                    return None
                plan = row_to_plan(row)
                cur.execute(
                    "SELECT * FROM outreach_recipients WHERE plan_id = %s",
                    (plan_id,),
                )
                recipient_rows = cur.fetchall()
            plan.recipients = [row_to_recipient(r) for r in recipient_rows]
            return plan
        finally:
            conn.close()

    def send(self, plan_id: str) -> OutreachSendResult:
        plan = self.load_plan(plan_id)
        if plan is None:
            return OutreachSendResult(
                plan_id=plan_id,
                delivered=0,
                stub=True,
                message="Plano de outreach não encontrado.",
            )
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE outreach_plans SET status = 'sent' WHERE id = %s",
                    (plan_id,),
                )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
        return OutreachSendResult(
            plan_id=plan_id,
            delivered=len(plan.recipients),
            stub=True,
            message=(
                f"Envio simulado concluído: {len(plan.recipients)} destinatário(s) "
                "marcado(s) como 'sent'."
            ),
        )

    def _save_plan(self, plan: OutreachPlan) -> None:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                plan_row = plan_to_row(plan)
                cur.execute(
                    "INSERT INTO outreach_plans (id, job_id, channel, message_template, status, created_at) "
                    "VALUES (%s, %s, %s, %s, %s, %s)",
                    tuple(plan_row[k] for k in ("id", "job_id", "channel", "message_template", "status", "created_at")),
                )
                for recipient in plan.recipients:
                    recipient_row = recipient_to_row(plan.id, recipient, str(uuid.uuid4()))
                    cur.execute(
                        "INSERT INTO outreach_recipients (id, plan_id, lead_id, name, contact, message) "
                        "VALUES (%s, %s, %s, %s, %s, %s)",
                        tuple(recipient_row[k] for k in ("id", "plan_id", "lead_id", "name", "contact", "message")),
                    )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()


def pick_contact(lead: Lead, channel: str) -> str | None:
    if channel == "email":
        for email in lead.emails:
            norm = normalize_email(email)
            if norm:
                return norm
        return None
    # whatsapp channel
    for wa in lead.whatsapp:
        if wa:
            return wa
    for phone in lead.phones:
        wa_link = build_wa_link(phone)
        if wa_link:
            return wa_link
    return None
