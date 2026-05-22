import requests
from sources import Article
from config import MEDIASTACK_API_KEY, MAX_ARTICLES_PER_SOURCE

MEDIASTACK_URL = "https://api.mediastack.com/v1/news"

def fetch() -> list[Article]:
    """Fetches fintech articles from the MediaStack news API."""
    if not MEDIASTACK_API_KEY:
        print("[MediaStack] WARNING: No API key configured, skipping.")
        return []

    params = {
        "access_key": MEDIASTACK_API_KEY,
        "keywords": "fintech,open banking,payments,neobank,DeFi,embedded finance",
        "languages": "en",
        "limit": MAX_ARTICLES_PER_SOURCE,
        "sort": "published_desc",
    }

    try:
        response = requests.get(MEDIASTACK_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        articles = []
        for item in data.get("data", []):
            title = item.get("title", "")
            summary = item.get("description", "")

            if not title or not summary:
                continue

            articles.append(Article(
                title=title,
                summary=summary[:300],
                url=item.get("url", ""),
                source="MediaStack",
                published_at=item.get("published_at", ""),
            ))

        print(f"[MediaStack] {len(articles)} artículos obtenidos.")
        return articles

    except requests.HTTPError as e:
        print(f"[MediaStack] HTTP {e.response.status_code}: {e.response.text[:200]}")
        return []
    except requests.RequestException as e:
        print(f"[MediaStack] Error al hacer fetch: {e}")
        return []
