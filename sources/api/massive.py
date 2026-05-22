import requests
from sources import Article
from config import MASSIVE_API_KEY, MAX_ARTICLES_PER_SOURCE

# TODO: verificar el endpoint exacto en https://massive.com/docs/rest
MASSIVE_BASE_URL = "https://api.massive.com"
NEWS_ENDPOINT = f"{MASSIVE_BASE_URL}/news"

def fetch() -> list[Article]:
    """Fetches fintech news from the Massive financial data API."""
    if not MASSIVE_API_KEY:
        print("[Massive] WARNING: No API key configured, skipping.")
        return []

    headers = {
        "Authorization": f"Bearer {MASSIVE_API_KEY}",
        "Accept": "application/json",
    }

    # TODO: ajustar params según la documentación REST de Massive
    params = {
        "limit": MAX_ARTICLES_PER_SOURCE,
        "category": "fintech",  # ajustar si el campo/valor es distinto
    }

    try:
        response = requests.get(NEWS_ENDPOINT, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        articles = []
        # TODO: ajustar la clave raíz del JSON según la respuesta real
        items = data if isinstance(data, list) else data.get("results", data.get("data", []))

        for item in items:
            title = item.get("title") or item.get("headline", "")
            summary = item.get("summary") or item.get("description") or item.get("body", "")
            url = item.get("url") or item.get("link", "")
            published_at = item.get("published_at") or item.get("date", "")

            if not title:
                continue

            articles.append(Article(
                title=title,
                summary=str(summary)[:300],
                url=url,
                source="Massive",
                published_at=str(published_at),
            ))

        print(f"[Massive] {len(articles)} artículos obtenidos.")
        return articles

    except requests.HTTPError as e:
        print(f"[Massive] HTTP {e.response.status_code}: {e.response.text[:200]}")
        return []
    except requests.RequestException as e:
        print(f"[Massive] Error al hacer fetch: {e}")
        return []
