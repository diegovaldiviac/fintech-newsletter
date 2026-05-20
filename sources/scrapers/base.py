"""
base.py — Clase base para todos los scrapers del proyecto.

Responsabilidades:
- Hacer el request HTTP con headers realistas
- Parsear el HTML con BeautifulSoup
- Rate limiting simple con sleep entre requests
- Manejo de errores consistente

Usa requests.Session() internamente — esto permite que AuthenticatedScraper
reutilice la misma sesión (con cookies) para todos los requests.

Cada scraper concreto hereda de BaseScraper e implementa `parse()`.
"""

import time
import requests
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
from sources import Article


# Headers que imitan un browser real — reduce bloqueos en sitios simples
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# Segundos de espera entre requests al mismo dominio
DEFAULT_SLEEP_SECONDS = 2


class BaseScraper(ABC):
    """
    Clase base para scrapers de HTML estático sin autenticación.

    Uso:
        class DiarioFinancieroScraper(BaseScraper):
            BASE_URL = "https://www.df.cl/tags/fintech/p/1"

            def parse(self, soup: BeautifulSoup) -> list[Article]:
                # lógica específica del DF
                ...

    Nota de diseño: usamos self.session (requests.Session) en vez de
    requests.get() directamente. Esto permite que AuthenticatedScraper
    sobreescriba la sesión con una autenticada, sin cambiar ninguna
    otra lógica de esta clase.
    """

    BASE_URL: str = ""
    SLEEP_SECONDS: int = DEFAULT_SLEEP_SECONDS

    def __init__(self):
        # Sesión base — sin auth, solo headers comunes
        # AuthenticatedScraper sobreescribe esto con una sesión autenticada
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)

    def fetch_html(self, url: str) -> BeautifulSoup | None:
        """
        Hace GET al URL usando self.session y retorna BeautifulSoup.
        Al usar self.session, si el scraper está autenticado las cookies
        van incluidas automáticamente sin ningún cambio en este método.
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, "lxml")

        except requests.HTTPError as e:
            print(f"[{self.__class__.__name__}] HTTP {e.response.status_code} en {url}")
            return None
        except requests.RequestException as e:
            print(f"[{self.__class__.__name__}] Error de red en {url}: {e}")
            return None

    def fetch_multiple(self, urls: list[str]) -> list[BeautifulSoup]:
        """
        Hace GET a múltiples URLs con sleep entre cada uno.
        Útil cuando necesitas entrar a cada artículo individualmente.
        """
        results = []
        for i, url in enumerate(urls):
            soup = self.fetch_html(url)
            if soup:
                results.append(soup)
            if i < len(urls) - 1:
                time.sleep(self.SLEEP_SECONDS)
        return results

    @abstractmethod
    def parse(self, soup: BeautifulSoup) -> list[Article]:
        """
        Lógica específica de cada sitio.
        Recibe el HTML parseado, retorna lista de Article.
        """
        ...

    def fetch(self) -> list[Article]:
        """
        Entry point público — mismo contrato que los módulos de API.
        """
        if not self.BASE_URL:
            raise NotImplementedError(f"{self.__class__.__name__} debe definir BASE_URL")

        print(f"[{self.__class__.__name__}] Scraping {self.BASE_URL}...")
        soup = self.fetch_html(self.BASE_URL)

        if not soup:
            print(f"[{self.__class__.__name__}] No se pudo obtener el HTML.")
            return []

        articles = self.parse(soup)
        print(f"[{self.__class__.__name__}] {len(articles)} artículos obtenidos.")
        return articles
