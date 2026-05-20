"""
authenticated.py — Clase base para scrapers que requieren login.

Extiende BaseScraper agregando:
- Login automático antes del primer fetch
- Manejo de credenciales desde variables de entorno
- Detección de sesión expirada con re-login automático
- Verificación de que el login fue exitoso

Los scrapers concretos que hereden de esta clase deben implementar:
- LOGIN_URL: str         — endpoint donde se hace el POST de credenciales
- LOGIN_PAYLOAD: dict    — campos del formulario de login (sin las credenciales)
- EMAIL_ENV: str         — nombre de la variable de entorno con el email
- PASSWORD_ENV: str      — nombre de la variable de entorno con la password
- is_authenticated()     — lógica para verificar si la sesión es válida
- parse()                — igual que en BaseScraper

Flujo interno:
    fetch() → _ensure_authenticated() → fetch_html() → parse()
                      ↓
              si no hay sesión → _login() → POST credenciales
                                          → requests.Session guarda la cookie
                                          → is_authenticated() verifica acceso
"""

import os
import requests
from bs4 import BeautifulSoup
from abc import abstractmethod
from sources.scrapers.base import BaseScraper, DEFAULT_HEADERS
from sources import Article


class AuthenticatedScraper(BaseScraper):
    """
    Clase base para scrapers que requieren login con email/password.

    Uso:
        class EconomistScraper(AuthenticatedScraper):
            BASE_URL    = "https://www.economist.com/finance-and-economics"
            LOGIN_URL   = "https://www.economist.com/api/auth/login"
            EMAIL_ENV   = "ECONOMIST_EMAIL"
            PASSWORD_ENV = "ECONOMIST_PASSWORD"

            def is_authenticated(self, soup: BeautifulSoup) -> bool:
                # Verifica que el HTML tiene contenido de suscriptor
                return soup.find("div", class_="article-body") is not None

            def parse(self, soup: BeautifulSoup) -> list[Article]:
                ...
    """

    # Subclases definen estos atributos
    LOGIN_URL: str = ""
    EMAIL_ENV: str = ""
    PASSWORD_ENV: str = ""

    # Campos extra del form de login que no son email/password
    # Ejemplo: {"remember_me": "true", "redirect": "/"}
    EXTRA_LOGIN_FIELDS: dict = {}

    def __init__(self):
        super().__init__()
        self._authenticated = False

    def _get_credentials(self) -> tuple[str, str]:
        """Lee credenciales desde variables de entorno."""
        email = os.getenv(self.EMAIL_ENV, "")
        password = os.getenv(self.PASSWORD_ENV, "")

        if not email or not password:
            raise ValueError(
                f"[{self.__class__.__name__}] Faltan credenciales. "
                f"Define {self.EMAIL_ENV} y {self.PASSWORD_ENV} en tu .env"
            )
        return email, password

    def _login(self) -> bool:
        """
        Hace POST al LOGIN_URL con las credenciales.
        requests.Session guarda automáticamente la cookie de sesión devuelta.
        Retorna True si el login fue exitoso.
        """
        if not self.LOGIN_URL:
            raise NotImplementedError(f"{self.__class__.__name__} debe definir LOGIN_URL")

        email, password = self._get_credentials()

        payload = {
            "email": email,
            "password": password,
            **self.EXTRA_LOGIN_FIELDS,
        }

        print(f"[{self.__class__.__name__}] Iniciando sesión en {self.LOGIN_URL}...")

        try:
            response = self.session.post(self.LOGIN_URL, data=payload, timeout=15)
            response.raise_for_status()

            # Verificar que la cookie de sesión fue recibida
            if not self.session.cookies:
                print(f"[{self.__class__.__name__}] Login POST exitoso pero no se recibieron cookies.")
                return False

            print(f"[{self.__class__.__name__}] Login exitoso.")
            return True

        except requests.HTTPError as e:
            print(f"[{self.__class__.__name__}] Login falló — HTTP {e.response.status_code}")
            return False
        except requests.RequestException as e:
            print(f"[{self.__class__.__name__}] Login falló — Error de red: {e}")
            return False

    @abstractmethod
    def is_authenticated(self, soup: BeautifulSoup) -> bool:
        """
        Verifica si la sesión actual tiene acceso a contenido de suscriptor.
        Cada sitio tiene su propia señal — un elemento del DOM, un redirect, etc.

        Ejemplo The Economist:
            return soup.find("div", {"data-test-id": "Article"}) is not None

        Ejemplo genérico:
            return "Log in" not in soup.get_text()
        """
        ...

    def _ensure_authenticated(self) -> bool:
        """
        Garantiza que hay una sesión válida antes de hacer fetch.
        Si no hay sesión, intenta hacer login.
        """
        if self._authenticated:
            return True

        success = self._login()
        self._authenticated = success
        return success

    def fetch(self) -> list[Article]:
        """
        Override del fetch() de BaseScraper.
        Agrega el paso de autenticación antes de hacer scraping.
        """
        if not self.BASE_URL:
            raise NotImplementedError(f"{self.__class__.__name__} debe definir BASE_URL")

        if not self._ensure_authenticated():
            print(f"[{self.__class__.__name__}] No se pudo autenticar. Saltando fuente.")
            return []

        print(f"[{self.__class__.__name__}] Scraping {self.BASE_URL}...")
        soup = self.fetch_html(self.BASE_URL)

        if not soup:
            print(f"[{self.__class__.__name__}] No se pudo obtener el HTML.")
            return []

        # Verificar que realmente tenemos acceso de suscriptor
        if not self.is_authenticated(soup):
            print(f"[{self.__class__.__name__}] Sesión expirada o acceso denegado. Reintentando login...")
            self._authenticated = False
            if not self._ensure_authenticated():
                print(f"[{self.__class__.__name__}] Re-login falló. Saltando fuente.")
                return []
            soup = self.fetch_html(self.BASE_URL)
            if not soup:
                return []

        articles = self.parse(soup)
        print(f"[{self.__class__.__name__}] {len(articles)} artículos obtenidos.")
        return articles
