import re
import requests
import resend
from datetime import datetime
from pathlib import Path
from config import RESEND_API_KEY, RESEND_AUDIENCE_ID, EMAIL_FROM

resend.api_key = RESEND_API_KEY

RESEND_API_BASE = "https://api.resend.com"


def get_audience_emails() -> list[str]:
    """Obtiene los emails activos de la Audience de Resend."""
    url = f"{RESEND_API_BASE}/audiences/{RESEND_AUDIENCE_ID}/contacts"
    headers = {"Authorization": f"Bearer {RESEND_API_KEY}"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        contacts = response.json().get("data", [])

        emails = [
            c["email"]
            for c in contacts
            if not c.get("unsubscribed", False)
        ]
        print(f"[Email] {len(emails)} suscriptores activos en la Audience.")
        return emails

    except requests.RequestException as e:
        print(f"[Email] Error al obtener contactos de la Audience: {e}")
        return []


def render_html(content: str) -> str:
    """Inserta el contenido generado por el LLM en el template HTML."""
    template_path = Path(__file__).parent.parent / "templates" / "newsletter.html"
    template = template_path.read_text(encoding="utf-8")

    # Convertir **texto** a <strong>
    parts = content.split("**")
    html_parts = [
        f"<strong>{part}</strong>" if i % 2 == 1 else part
        for i, part in enumerate(parts)
    ]
    html_content = "".join(html_parts)

    # Convertir URLs en links clicables
    html_content = re.sub(r'(https?://[^\s\)<>]+)', r'<a href="\1">\1</a>', html_content)

    date_str = datetime.now().strftime("%d %b %Y")
    return template.replace("{content}", html_content).replace("{date}", date_str)


def send(newsletter_text: str) -> bool:
    """Obtiene suscriptores de la Audience y envía el newsletter a cada uno."""
    if not RESEND_API_KEY or not EMAIL_FROM or not RESEND_AUDIENCE_ID:
        print("[Email] ERROR: Faltan variables de entorno (RESEND_API_KEY, EMAIL_FROM, RESEND_AUDIENCE_ID).")
        return False

    emails = get_audience_emails()
    if not emails:
        print("[Email] No hay suscriptores activos. Abortando envío.")
        return False

    html_body = render_html(newsletter_text)
    date_str = datetime.now().strftime("%d %b %Y")
    subject = f"Fintech Signal — {date_str}"

    failed = 0
    for email in emails:
        try:
            response = resend.Emails.send({
                "from": f"Diego Valdivia <{EMAIL_FROM}>",
                "to": [email],
                "subject": subject,
                "html": html_body,
                "headers": {
                    "List-Unsubscribe": f"<mailto:unsubscribe@diegovaldiviacox.com?subject=unsubscribe>",
                    "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
                },
            })
            print(f"[Email] Enviado a {email} — ID: {response['id']}")
        except Exception as e:
            print(f"[Email] Error al enviar a {email}: {e}")
            failed += 1

    success = failed == 0
    if not success:
        print(f"[Email] {failed}/{len(emails)} envíos fallaron.")
    return success
