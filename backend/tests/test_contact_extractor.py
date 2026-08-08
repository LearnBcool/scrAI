from __future__ import annotations

from app.services.extraction.contact_extractor import extract_contacts

SAMPLE = """
<title>Pizzaria Bella Napoli</title>
Fale conosco pelo email contato@bellanapoli.com.br ou sac@bellanapoli.com.br
Telefone: (11) 91234-5678 e fixo (11) 3456-7890
WhatsApp: https://wa.me/5511912345678
Siga no Instagram: https://www.instagram.com/bellanapoli
LinkedIn: https://linkedin.com/company/bellanapoli
Site: https://www.bellanapoli.com.br
"""


def test_extract_emails():
    info = extract_contacts(SAMPLE)
    assert "contato@bellanapoli.com.br" in info.emails
    assert "sac@bellanapoli.com.br" in info.emails


def test_extract_phones():
    info = extract_contacts(SAMPLE)
    assert "11912345678" in info.phones
    assert "1134567890" in info.phones


def test_extract_whatsapp():
    info = extract_contacts(SAMPLE)
    assert "https://wa.me/5511912345678" in info.whatsapp


def test_extract_social_and_website():
    info = extract_contacts(SAMPLE)
    assert info.instagram == "https://instagram.com/bellanapoli"
    assert info.linkedin == "https://linkedin.com/company/bellanapoli"
    assert info.website and "bellanapoli.com.br" in info.website


def test_mailto_links():
    text = '<a href="mailto:foo@bar.com.br">email</a>'
    info = extract_contacts(text)
    assert "foo@bar.com.br" in info.emails


def test_api_whatsapp_link():
    text = "WhatsApp: https://api.whatsapp.com/send?phone=5511987654321"
    info = extract_contacts(text)
    assert "https://wa.me/5511987654321" in info.whatsapp


def test_wa_number_not_counted_as_phone():
    info = extract_contacts(SAMPLE)
    assert "11912345678" in info.phones  # from "(11) 91234-5678"
    assert info.phones.count("11912345678") == 1


def test_at_handles_fallback_to_instagram():
    info = extract_contacts("Siga @bellanapoli no Insta")
    assert info.instagram == "https://instagram.com/bellanapoli"
