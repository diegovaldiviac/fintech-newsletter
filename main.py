"""
main.py — Entry point para correr el pipeline manualmente.

Uso:
    python main.py            # Corre el pipeline completo y envía el email
    python main.py --dry-run  # Genera el newsletter pero NO envía el email
"""

import sys

# --- Fuentes API (activas) ---
from sources.api import newsapi, guardian, reddit, massive, mediastack

# --- Fuentes Scraper (pendientes — no corren aún) ---
# TODO: descomentar cuando el scraper del DF esté listo
# from sources.scrapers.mercadolibre import MercadoLibreTechScraper
# from sources.scrapers.diario_financiero import DiarioFinancieroScraper
# from sources.scrapers.economist import EconomistScraper

from pipeline import filter, llm, email


def run(dry_run: bool = False):
    print("\n🚀 Iniciando pipeline de Fintech Signal Newsletter...\n")

    # 1. Ingesta de datos
    print("── PASO 1: Fetch de fuentes ──")
    articles = []

    # APIs activas
    articles += newsapi.fetch()
    articles += guardian.fetch()
    #articles += reddit.fetch()
    #articles += massive.fetch()
    #articles += mediastack.fetch()

    # Scrapers — descomenta cuando estén listos
    # articles += MercadoLibreTechScraper().fetch()
    # articles += DiarioFinancieroScraper().fetch()
    # articles += EconomistScraper().fetch()

    print(f"   Total artículos crudos: {len(articles)}\n")

    if not articles:
        print("❌ No se obtuvieron artículos. Verifica tus API keys en .env")
        return

    # 2. Filtrar y deduplicar
    print("── PASO 2: Filtrado y deduplicación ──")
    filtered = filter.run(articles, max_total=10)
    print(f"   Artículos listos para el LLM: {len(filtered)}\n")

    if not filtered:
        print("❌ Ningún artículo pasó el filtro. Ajusta los keywords en config.py")
        return

    # 3. Generar newsletter con Claude
    print("── PASO 3: Generación con LLM ──")
    newsletter_text = llm.generate(filtered)
    print()

    # Preview en consola siempre
    print("── PREVIEW DEL NEWSLETTER ──")
    print("-" * 60)
    print(newsletter_text)
    print("-" * 60)
    print()

    # 4. Enviar email
    if dry_run:
        print("── [DRY RUN] Email NO enviado. ──")
        print("   Corre sin --dry-run para enviar.\n")
    else:
        print("── PASO 4: Envío de email ──")
        success = email.send(newsletter_text)
        if success:
            print("\n✅ Pipeline completado exitosamente.")
        else:
            print("\n⚠️  Newsletter generado pero el email falló. Revisa config de Resend.")


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    run(dry_run=dry_run)
