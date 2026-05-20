import anthropic
from sources import Article
from config import ANTHROPIC_API_KEY

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """Eres el editor técnico de un newsletter semanal de innovación fintech.
Tu audiencia son ingenieros de software con experiencia en sistemas financieros.
Tu tono es directo, técnico, sin relleno corporativo. Vas al grano.
No usas frases como "en el dinámico mundo de..." o "es importante destacar que...".
Escribes en español, pero mantienes términos técnicos en inglés cuando corresponde (API, pipeline, latency, etc.).
"""

def build_prompt(articles: list[Article]) -> str:
    articles_text = ""
    for i, article in enumerate(articles, 1):
        articles_text += f"""
---
Artículo {i}
Título: {article.title}
Fuente: {article.source}
Resumen: {article.summary}
URL: {article.url}
"""

    return f"""Tienes los siguientes artículos de la semana sobre innovación fintech y tecnología financiera:

{articles_text}

---

Con base en estos artículos, redacta un newsletter semanal con la siguiente estructura:

1. **Intro** (2-3 líneas): Una frase directa sobre el tema dominante de la semana en fintech. Sin saludos genéricos.

2. **Top historias** (3-5 artículos): Para cada uno:
   - Título en negrita
   - 2-4 líneas explicando el "so what" técnico: qué tecnología está en juego, qué problema resuelve, por qué importa para un ingeniero
   - Link al artículo original

3. **Signal de la semana** (1 párrafo): Una tendencia técnica emergente que se desprende de las noticias. Puede ser un patrón arquitectónico, un cambio de paradigma, una tecnología que está ganando tracción.

4. **Cierre** (1 línea): Directo y sin florituras.

El newsletter completo no debe superar 500 palabras. Prioriza densidad de información sobre volumen.
"""

def generate(articles: list[Article]) -> str:
    """Calls Claude API and returns the newsletter as a string."""
    print("[LLM] Generando newsletter con Claude...")

    prompt = build_prompt(articles)

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
        system=SYSTEM_PROMPT,
    )

    content = message.content[0].text
    print("[LLM] Newsletter generado exitosamente.")
    return content
