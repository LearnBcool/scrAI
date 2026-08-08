from __future__ import annotations

from app.schemas.lead import Lead

EMAIL_CHANNEL = "email"
WHATSAPP_CHANNEL = "whatsapp"
VALID_CHANNELS = (EMAIL_CHANNEL, WHATSAPP_CHANNEL)

DEFAULT_EMAIL_TEMPLATE = (
    "Olá {name},\n\n"
    "Encontrei a sua empresa do segmento de {segment} em {city} e gostaria de "
    "apresentar uma proposta de parceria. Podemos conversar?\n\n"
    "Atenciosamente,\nEquipe de Prospecção"
)

DEFAULT_WHATSAPP_TEMPLATE = (
    "Olá {name}! Vi que vocês atuam em {segment} na região de {city} e gostaria "
    "de conversar sobre uma oportunidade de parceria. Pode me responder por aqui?"
)


def validate_channel(channel: str) -> str:
    normalized = (channel or "").strip().lower()
    if normalized not in VALID_CHANNELS:
        raise ValueError(
            f"Canal inválido: '{channel}'. Use 'email' ou 'whatsapp'."
        )
    return normalized


def default_template_for(channel: str) -> str:
    if channel == EMAIL_CHANNEL:
        return DEFAULT_EMAIL_TEMPLATE
    return DEFAULT_WHATSAPP_TEMPLATE


def render_template(template: str, lead: Lead) -> str:
    return (
        (template or "")
        .replace("{name}", lead.name or "")
        .replace("{segment}", lead.segment or "")
        .replace("{city}", lead.city or "")
    )
