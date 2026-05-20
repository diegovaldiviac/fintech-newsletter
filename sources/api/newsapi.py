import requests
from sources import Article
from config import NEWSAPI_KEY, NEWSAPI_QUERY, MAX_ARTICLES_PER_SOURCE

NEWSAPI_URL = "https://newsapi.org/v2/everything"

def fetch() -> list[Article]:
    """Fetches fintech articles from NewsAPI from the last 7 days."""
    if not NEWSAPI_KEY:
        print("[NewsAPI] WARNING: No API key configured, skipping.")
        return []

    params = {
        "q": NEWSAPI_QUERY,
        "language": "en",          # Fuentes en inglés; el LLM traduce y resume en español
        "sortBy": "relevancy",
        "pageSize": MAX_ARTICLES_PER_SOURCE,
        "apiKey": NEWSAPI_KEY,
    }

    try:
        response = requests.get(NEWSAPI_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        articles = []
        for item in data.get("articles", []):
            # Ignorar artículos sin contenido útil
            if not item.get("title") or not item.get("description"):
                continue
            if "[Removed]" in item.get("title", ""):
                continue

            articles.append(Article(
                title=item["title"],
                summary=item.get("description", ""),
                url=item.get("url", ""),
                source="NewsAPI",
                published_at=item.get("publishedAt", ""),
            ))

        print(f"[NewsAPI] {len(articles)} artículos obtenidos.")
        return articles

    except requests.RequestException as e:
        print(f"[NewsAPI] Error al hacer fetch: {e}")
        return []
