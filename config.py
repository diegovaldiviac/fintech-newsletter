from dotenv import load_dotenv
import os

load_dotenv()

# Fuentes
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
GUARDIAN_API_KEY = os.getenv("GUARDIAN_API_KEY")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "fintech-newsletter/1.0")

# LLM
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Email
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_TO = os.getenv("EMAIL_TO")

# Pipeline
MAX_ARTICLES_PER_SOURCE = int(os.getenv("MAX_ARTICLES_PER_SOURCE", 5))

# Keywords para filtrar contenido relevante
FINTECH_KEYWORDS = [
    "fintech", "open banking", "blockchain", "payments",
    "regtech", "insurtech", "wealthtech", "neobank",
    "API financiera", "inteligencia artificial finanzas",
    "machine learning trading", "DeFi", "embedded finance"
]

NEWSAPI_QUERY = "fintech OR (artificial intelligence finance) OR (open banking) OR (payments innovation)"
GUARDIAN_QUERY = "fintech OR financial-technology OR digital-banking"
REDDIT_SUBREDDITS = ["fintech", "algotrading", "MachineLearning"]
