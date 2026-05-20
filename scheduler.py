"""
scheduler.py — Corre el pipeline automáticamente cada semana.

Uso:
    python scheduler.py

Corre el newsletter todos los lunes a las 8:00 AM.
Deja este proceso corriendo en background (o en tu servidor).
"""

from apscheduler.schedulers.blocking import BlockingScheduler
from main import run
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

scheduler = BlockingScheduler()

# Todos los lunes a las 8:00 AM (hora local del servidor)
@scheduler.scheduled_job("cron", day_of_week="mon", hour=8, minute=0)
def weekly_newsletter():
    log.info("⏰ Scheduler activado — corriendo pipeline semanal...")
    run(dry_run=False)

if __name__ == "__main__":
    print("📅 Scheduler iniciado. El newsletter se enviará cada lunes a las 8:00 AM.")
    print("   Ctrl+C para detener.\n")
    scheduler.start()
