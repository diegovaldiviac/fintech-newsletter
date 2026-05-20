import resend
from datetime import datetime
from pathlib import Path
from config import RESEND_API_KEY, EMAIL_FROM, EMAIL_TO

resend.api_key = RESEND_API_KEY

def render_html(content: str) -> str:
    """Inserta el contenido generado por el LLM en el template HTML."""
    template_path = Path(__file__).parent.parent / "templates" / "newsletter.html"
    template = template_path.read_text(encoding="utf-8")

    # Convertir markdown básico a HTML
    html_content = content
    html_content = html_content.replace("**", "<strong>", 1)
    # Alternamos apertura y cierre de strong tags
    toggle = True
    result = []
    for char in content:
        result.append(char)
    # Enfoque más simple: reemplazar ** con tags alternados
    parts = content.split("**")
    html_parts = []
    for i, part in enumerate(parts):
        if i % 2 == 1:
            html_parts.append(f"<strong>{part}</strong>")
        else:
            html_parts.append(part)
    html_content = "".join(html_parts)

    # Convertir URLs en links clicables
    import re
    url_pattern = r'(https?://[^\s\)]+)'
    html_content = re.sub(url_pattern, r'<a href="\1">\1</a>', html_content)

    date_str = datetime.now().strftime("%d %b %Y")
    html = template.replace("{content}", html_content).replace("{date}", date_str)
    return html

def send(newsletter_text: str) -> bool:
    """Envía el newsletter por email usando Resend."""
    if not RESEND_API_KEY or not EMAIL_FROM or not EMAIL_TO:
        print("[Email] ERROR: Faltan variables de entorno para email.")
        return False

    html_body = render_html(newsletter_text)
    date_str = datetime.now().strftime("%d %b %Y")

    try:
        response = resend.Emails.send({
            "from": EMAIL_FROM,
            "to": [EMAIL_TO],
            "subject": f"⚡ Fintech Signal — {date_str}",
            "html": html_body,
        })
        print(f"[Email] Enviado exitosamente. ID: {response['id']}")
        return True

    except Exception as e:
        print(f"[Email] Error al enviar: {e}")
        return False
