"""
rss.py — Clase base para scrapers que consumen feeds RSS o Atom.

Es la estrategia más limpia para fuentes que exponen feeds:
- No depende de estructura HTML (no se rompe con rediseños)
- No requiere autenticación
- feedparser maneja RSS 1.0, RSS 2.0 y Atom automáticamente

Cada scraper concreto solo necesita definir:
- FEED_URL: str          — URL del feed RSS/Atom
- SOURCE_NAME: str       — Nombre legible para el campo Article.source
- filter_entry()         — Opcional: filtrar entradas por relevancia

Uso:
    class MercadoLibreTechScraper(RSSBaseScraper):
        FEED_URL    = "https://medium.com/feed/mercadolibre-tech"
        SOURCE_NAME = "MercadoLibre Tech Blog"
"""

import feedparser
from abc import ABC
from sources import Article
from config import MAX_ARTICLES_PER_SOURCE


class RSSBaseScraper(ABC):
    """
    Clase base para fuentes RSS/Atom.

    A diferencia de BaseScraper (que trabaja con BeautifulSoup),
    esta clase usa feedparser directamente — no hay HTML que parsear.

    No hereda de BaseScraper intencionalmente: el mecanismo de acceso
    es completamente distinto (feed vs HTTP + DOM). Ambas clases comparten
    el mismo contrato público: fetch() -> list[Article].
    """

    FEED_URL: str = ""
    SOURCE_NAME: str = ""
    MAX_ENTRIES: int = MAX_ARTICLES_PER_SOURCE

    def filter_entry(self, entry: feedparser.FeedParserDict) -> bool:
        """
        Override opcional para filtrar entradas del feed.
        Por defecto acepta todas.

        Ejemplo — solo entradas con tag 'fintech':
            def filter_entry(self, entry):
                tags = [t.term.lower() for t in getattr(entry, 'tags', [])]
                return 'fintech' in tags
        """
        return True

    def parse_entry(self, entry: feedparser.FeedParserDict) -> Article | None:
        """
        Convierte una entrada del feed en un Article.
        Override si el feed tiene una estructura no estándar.
        """
        title   = entry.get("title", "").strip()
        url     = entry.get("link", "").strip()
        summary = entry.get("summary", "") or entry.get("description", "")

        # feedparser puede devolver HTML en el summary — limpieza básica
        if summary:
            from bs4 import BeautifulSoup
            summary = BeautifulSoup(summary, "lxml").get_text(separator=" ").strip()
            # Truncar a 300 chars — suficiente para el LLM
            summary = summary[:300]

        published = entry.get("published", "") or entry.get("updated", "")

        if not title or not url:
            return None

        return Article(
            title=title,
            summary=summary,
            url=url,
            source=self.SOURCE_NAME or self.__class__.__name__,
            published_at=published,
        )

    def fetch(self) -> list[Article]:
        """
        Entry point público — mismo contrato que BaseScraper y módulos API.
        Parsea el feed y retorna lista de Article.
        """
        if not self.FEED_URL:
            raise NotImplementedError(f"{self.__class__.__name__} debe definir FEED_URL")

        print(f"[{self.__class__.__name__}] Leyendo feed {self.FEED_URL}...")

        feed = feedparser.parse(self.FEED_URL)

        # feedparser no lanza excepciones — reporta errores en feed.bozo
        if feed.bozo:
            print(f"[{self.__class__.__name__}] Advertencia al parsear feed: {feed.bozo_exception}")

        if not feed.entries:
            print(f"[{self.__class__.__name__}] Feed vacío o inaccesible.")
            return []

        articles = []
        for entry in feed.entries:
            if len(articles) >= self.MAX_ENTRIES:
                break
            if not self.filter_entry(entry):
                continue
            article = self.parse_entry(entry)
            if article:
                articles.append(article)

        print(f"[{self.__class__.__name__}] {len(articles)} artículos obtenidos.")
        return articles
