# ⚡ Fintech Signal Newsletter

Pipeline automatizado que recopila señales de innovación fintech desde APIs públicas, las procesa con Claude (LLM) y las envía como newsletter semanal por email.

---

## Stack

| Capa | Tecnología |
|---|---|
| Lenguaje | Python 3.11+ |
| Fuentes | NewsAPI, The Guardian API, Reddit (PRAW) |
| LLM | Claude API (Anthropic) |
| Email | Resend |
| Scheduling | APScheduler |
| Hosting (futuro) | Railway |

---

## Setup Local

### 1. Clonar e instalar dependencias

```bash
git clone <repo>
cd fintech-newsletter
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
# Edita .env con tus API keys reales
```

**APIs que necesitas:**
- **NewsAPI:** https://newsapi.org (gratis, 100 req/día)
- **The Guardian:** https://open-platform.theguardian.com (gratis)
- **Reddit:** https://www.reddit.com/prefs/apps → crear app "script"
- **Anthropic:** https://console.anthropic.com
- **Resend:** https://resend.com (3.000 emails/mes gratis)

### 3. Correr manualmente

```bash
# Dry run — genera el newsletter y lo muestra en consola, NO envía email
python main.py --dry-run

# Correr completo — genera Y envía el email
python main.py
```

### 4. Activar scheduler semanal

```bash
# Corre el proceso en background (envía cada lunes 8:00 AM)
python scheduler.py
```

---

## Estructura del Proyecto

```
fintech-newsletter/
├── .env                    # API keys (no subir al repo)
├── .env.example            # Template de variables
├── requirements.txt
├── config.py               # Configuración central y keywords
│
├── sources/                # Módulos de ingesta por fuente
│   ├── __init__.py         # Modelo Article (Pydantic)
│   ├── newsapi.py
│   ├── guardian.py
│   └── reddit.py
│
├── pipeline/               # Procesamiento
│   ├── filter.py           # Deduplicación y filtrado por keywords
│   ├── llm.py              # Generación con Claude API
│   └── email.py            # Renderizado HTML y envío con Resend
│
├── templates/
│   └── newsletter.html     # Template visual del email
│
├── main.py                 # Entry point manual
└── scheduler.py            # Scheduler semanal automático
```

---

## Plan de Hosting (Railway)

1. Subir repo a GitHub
2. Crear proyecto en https://railway.app
3. Conectar repositorio
4. Agregar variables de entorno en Railway (las mismas del .env)
5. Cambiar el start command a: `python scheduler.py`
6. Deploy — Railway mantiene el proceso corriendo 24/7

Costo estimado: ~$5 USD/mes en el plan Hobby de Railway.

---

## Próximos pasos (post-MVP)

- [ ] Agregar scraping de Finextra y a16z blog
- [ ] Soporte para lista de suscriptores (CSV o base de datos simple)
- [ ] Dashboard web para ver historial de newsletters generados
- [ ] Feedback loop: tracking de clicks para mejorar selección de artículos
