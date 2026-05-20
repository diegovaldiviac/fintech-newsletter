import requests
from sources import Article
from config import GUARDIAN_API_KEY, GUARDIAN_QUERY, MAX_ARTICLES_PER_SOURCE

GUARDIAN_URL = "https://content.guardianapis.com/search"

def fetch() -> list[Article]:
    """Fetches fintech articles from The Guardian API."""
    if not GUARDIAN_API_KEY:
        print("[Guardian] WARNING: No API key configured, skipping.")
        return []

    params = {
        "q": GUARDIAN_QUERY,
        "section": "technology|business|money",
        "show-fields": "trailText",       # Resumen corto del artículo
        "order-by": "relevance",
        "page-size": MAX_ARTICLES_PER_SOURCE,
        "api-key": GUARDIAN_API_KEY,
    }

    try:
        response = requests.get(GUARDIAN_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        results = data.get("response", {}).get("results", [])
        articles = []

        for item in results:
            fields = item.get("fields", {})
            summary = fields.get("trailText", "")

            # Limpiar HTML básico del trailText
            summary = summary.replace("<p>", "").replace("</p>", "").strip()

            articles.append(Article(
                title=item.get("webTitle", ""),
                summary=summary,
                url=item.get("webUrl", ""),
                source="The Guardian",
                published_at=item.get("webPublicationDate", ""),
            ))

        print(f"[Guardian] {len(articles)} artículos obtenidos.")
        return articles

    except requests.RequestException as e:
        print(f"[Guardian] Error al hacer fetch: {e}")
        return []
