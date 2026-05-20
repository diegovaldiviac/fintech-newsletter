"""
mercadolibre.py — Scraper del blog técnico de MercadoLibre.

Fuente: https://medium.com/mercadolibre-tech
Feed:   https://medium.com/feed/mercadolibre-tech

El blog cubre arquitectura, ML, mobile, data y fintech desde
el equipo de ingeniería de la empresa más grande de Latam.
Publicaciones en inglés y español.
"""

import feedparser
from sources.scrapers.rss import RSSBaseScraper

# Keywords técnicos relevantes para el newsletter
# El blog también publica sobre mobile, cultura, etc. — los filtramos
RELEVANT_TAGS = {
    "fintech", "payments", "machine learning", "data", "architecture",
    "platform", "api", "backend", "infrastructure", "ai", "security",
    "mercadopago", "open source", "cloud", "microservices",
}


class MercadoLibreTechScraper(RSSBaseScraper):
    FEED_URL    = "https://medium.com/feed/mercadolibre-tech"
    SOURCE_NAME = "MercadoLibre Tech Blog"

    def filter_entry(self, entry: feedparser.FeedParserDict) -> bool:
        """
        Filtra entradas por relevancia técnica.
        Acepta el artículo si al menos uno de sus tags coincide
        con RELEVANT_TAGS, o si no tiene tags (los incluimos por default).
        """
        entry_tags = [t.term.lower() for t in getattr(entry, "tags", [])]

        # Sin tags → incluir (mejor abarcar más que perder artículos)
        if not entry_tags:
            return True

        return bool(set(entry_tags) & RELEVANT_TAGS)
