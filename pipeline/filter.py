from sources import Article
from config import FINTECH_KEYWORDS

def deduplicate(articles: list[Article]) -> list[Article]:
    """Elimina artículos duplicados por título similar."""
    seen_titles = set()
    unique = []

    for article in articles:
        # Normalizar título para comparación
        normalized = article.title.lower().strip()
        if normalized not in seen_titles:
            seen_titles.add(normalized)
            unique.append(article)

    return unique

def filter_relevant(articles: list[Article]) -> list[Article]:
    """Filtra artículos que contienen keywords relevantes de fintech."""
    relevant = []

    for article in articles:
        text = f"{article.title} {article.summary}".lower()
        if any(kw.lower() in text for kw in FINTECH_KEYWORDS):
            relevant.append(article)

    return relevant

def run(articles: list[Article], max_total: int = 10) -> list[Article]:
    """Pipeline completo: deduplicar → filtrar → limitar cantidad."""
    articles = deduplicate(articles)
    articles = filter_relevant(articles)
    articles = articles[:max_total]

    print(f"[Filter] {len(articles)} artículos después de filtrar y deduplicar.")
    return articles
