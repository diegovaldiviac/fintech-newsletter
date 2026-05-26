# Fintech Signal Newsletter

Automated pipeline that collects fintech innovation signals from public APIs, processes them with an LLM, and delivers a weekly newsletter by email — with no server required.

---

## Subscribe

Want to receive the newsletter? Head over to **[diegovaldiviacox.com](https://diegovaldiviacox.com)** and sign up.

---

## How it runs — serverless via GitHub Actions

The pipeline runs entirely on GitHub Actions on a weekly cron schedule. No server, no hosting costs.

```yaml
on:
  schedule:
    - cron: '0 12 * * 1'  # Every Monday at 12:00 UTC
  workflow_dispatch:        # Can also be triggered manually from GitHub
```

Every Monday, GitHub spins up a runner that:
1. Fetches articles from all configured sources
2. Filters and deduplicates by fintech relevance
3. Generates the newsletter with an LLM
4. Reads the subscriber list from Resend Audiences
5. Sends the email to each active subscriber

You can also trigger it manually at any time from the **Actions** tab in GitHub.

---

## Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10 |
| Sources | NewsAPI, The Guardian, MediaStack |
| LLM | OpenAI GPT-4o (Anthropic Claude as fallback) |
| Email | Resend |
| Scheduling | GitHub Actions (cron) |
| Subscribers | Resend Audiences |

---

## Local Setup

### 1. Clone and install

```bash
git clone https://github.com/diegovaldiviac/fintech-newsletter
cd fintech-newsletter
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Fill in your API keys
```

### 3. Run locally

```bash
# Dry run — generates the newsletter and prints it, does NOT send email
python main.py --dry-run

# Full run — generates and sends
python main.py
```

---

## Required API Keys

Add these as **GitHub Actions secrets** (Settings → Secrets and variables → Actions) and in your local `.env`.

| Secret | Where to get it |
|--------|----------------|
| `OPENAI_API_KEY` | [platform.openai.com](https://platform.openai.com) |
| `RESEND_API_KEY` | [resend.com/api-keys](https://resend.com/api-keys) — requires Full Access |
| `RESEND_AUDIENCE_ID` | [resend.com/audiences](https://resend.com/audiences) |
| `EMAIL_FROM` | A verified domain in Resend (e.g. `newsletter@yourdomain.com`) |
| `NEWSAPI_KEY` | [newsapi.org](https://newsapi.org) — free, 100 req/day |
| `GUARDIAN_API_KEY` | [open-platform.theguardian.com](https://open-platform.theguardian.com) — free |
| `MEDIASTACK_API_KEY` | [mediastack.com](https://mediastack.com) — free tier available |
| `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com) — optional fallback |

---

## Switching LLM provider

The pipeline supports OpenAI and Anthropic. Set the provider in your `.env` or GitHub secret:

```
LLM_PROVIDER=openai   # default
LLM_PROVIDER=anthropic
```
