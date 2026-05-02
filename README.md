<div align="center">

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│   ╔╦╗╔═╗╦  ╔═╗╔═╗╦═╗╔═╗╔╦╗  ╔╗ ╔═╗╔╦╗                  │
│    ║ ║╣ ║  ║╣ ║ ╦╠╦╝╠═╣║║║  ╠╩╗║ ║ ║                   │
│    ╩ ╚═╝╩═╝╚═╝╚═╝╩╚═╩ ╩╩ ╩  ╚═╝╚═╝ ╩                   │
│                                                         │
│        a u t o n o m o u s   ·   r o b u s t            │
│              ·   f u n n y   d u d e   ·                │
└─────────────────────────────────────────────────────────┘
```

# 🤖 telegramBot

**A self-driving, plug-and-play, slightly-funny Telegram bot.**
Wire it to any REST API or website, give it a personality, and let it run.

[![CI](https://github.com/pgwiz/telegramBot/actions/workflows/ci.yml/badge.svg)](https://github.com/pgwiz/telegramBot/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.11%2B-blue?logo=python&logoColor=white)
![Telegram](https://img.shields.io/badge/python--telegram--bot-21.x-26A5E4?logo=telegram&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-production--ready-success)

[Quickstart](#-quickstart) ·
[Commands](#-command-reference) ·
[Plugins](#-build-your-own-integration) ·
[Architecture](#%EF%B8%8F-architecture) ·
[Deploy](#-deploy)

</div>

---

## ✨ Why this bot?

| Feature | What it means |
|---|---|
| 🛡️ **Robust** | Exponential-backoff retries, central error handler, crash-isolated jobs, structured logging. A single bad message can't take it down. |
| 🤹 **Personality** | `funny` / `pro` / `chill` modes, a curated joke + roast pool, optional LLM brain (OpenAI / Groq / any OpenAI-compatible endpoint). Falls back to canned banter offline. |
| 🔌 **Pluggable** | Drop a Python file in `src/integrations/`, subclass `Integration`, done. Auto-discovered at startup. |
| 🌐 **API & Web aware** | Built-ins for weather, crypto, generic REST `/fetch`, and `/scrape <url> <regex>`. Wire to anything. |
| 🤖 **Autonomous** | APScheduler-backed background loop: heartbeat, daily fact, subscription expiry sweep, custom cron jobs. |
| 🔐 **Multi-tier** | Existing admin / premium / group / normal user system, file manager, promo codes, action-group notifications. |
| 🐳 **Anywhere** | Run via `python`, `docker compose up`, or `worker: python src/bot.py` on a Procfile host (Railway, Heroku, Fly). |

---

## 🚀 Quickstart

### 1. Clone & configure

```bash
git clone https://github.com/pgwiz/telegramBot.git
cd telegramBot
cp .env.example .env
# Edit .env — at minimum: TELEGRAM_BOT_TOKEN and BOT_OWNER_ID
```

> Get your token from [@BotFather](https://t.me/BotFather). Get your numeric Telegram id from [@userinfobot](https://t.me/userinfobot).

### 2. Run it

<details open>
<summary><b>Local Python (recommended for dev)</b></summary>

```bash
make dev          # creates .venv and installs dev deps
make run          # starts the bot
```
</details>

<details>
<summary><b>Docker Compose</b></summary>

```bash
docker compose up --build
```

DB persists in `./data/bot.db`. Logs stream to stdout.
</details>

<details>
<summary><b>Procfile (Railway / Heroku / Fly)</b></summary>

The repo ships a `Procfile`. Push the repo, set env vars, and the platform will run `python src/bot.py` as a worker dyno/process.
</details>

### 3. Say hi

In Telegram: `/start` → `/help` → `/joke` → `/weather Nairobi` → `/price btc`.

---

## 🎮 Command reference

### Core

| Command | What it does |
|---|---|
| `/start` | Register / refresh your account |
| `/help` | Pretty menu of all commands |
| `/vibe funny\|pro\|chill` | Switch the bot's personality (per-user) |
| `/ping` | Health check |

### Fun

| Command | What it does |
|---|---|
| `/joke` | A clean dad joke |
| `/roast` | Light-hearted roast |
| `/fact` | Random fun fact |
| `/ask <text>` | Asks the configured LLM (or offline banter if none) |

### Integrations

| Command | What it does |
|---|---|
| `/integrations` | List loaded plugins |
| `/weather <city>` | Open-Meteo current weather (no key needed) |
| `/price <symbol>` | CoinGecko price (`btc`, `eth`, `sol`, …) |
| `/fetch <url>` | GET any URL, returns pretty JSON / text |
| `/scrape <url> [regex]` | Strip HTML and optionally regex-match |

### File manager (existing)

| Command | What it does |
|---|---|
| `/files` | Browse files you have access to |
| `/premium` | Premium menu |
| `/group` | Group menu |
| `/subscription` | Days remaining |
| `/renew` | Send renewal request to action group |
| `/feedback <text>` | Send feedback to action group |

### Admin

| Command | What it does |
|---|---|
| `/admin` | Admin panel |
| `/generate_promo <label> <days>` | Mint a new promo code |

---

## 🧠 Personality

The personality engine lives in `src/personality.py`. It has three modes:

```
DEFAULT_VIBE=funny   # 😎 default, witty
DEFAULT_VIBE=pro     # 📐 precise, professional, no fluff
DEFAULT_VIBE=chill   # ✌️  warm, casual
```

Each user can override their own vibe via `/vibe`.

**Optional LLM brain.** Drop an API key into `.env`:

```ini
LLM_PROVIDER=openai            # or "groq", or any OpenAI-compatible vendor
LLM_API_KEY=sk-...
LLM_MODEL=gpt-4o-mini
LLM_BASE_URL=                  # e.g. https://api.groq.com/openai/v1
```

If unset, `/ask` quietly falls back to the offline banter pool. The bot stays fun even with no network to an LLM.

---

## 🔌 Build your own integration

A plugin is one file. Drop it in `src/integrations/`:

```python
# src/integrations/github_stars.py
import httpx
from settings import get_settings
from . import Integration, IntegrationResult, register


class GitHubStarsIntegration(Integration):
    name = "stars"
    description = "Star count for any GitHub repo"
    usage = "/stars <owner/repo>"

    async def run(self, *args):
        if not args:
            return IntegrationResult(False, "Usage: /stars owner/repo")
        owner_repo = args[0]
        async with httpx.AsyncClient(timeout=get_settings().http_timeout) as client:
            r = await client.get(f"https://api.github.com/repos/{owner_repo}")
            r.raise_for_status()
            stars = r.json().get("stargazers_count", 0)
        return IntegrationResult(True, f"⭐ *{owner_repo}* — {stars:,} stars")


register(GitHubStarsIntegration())
```

Then register a command in `src/bot.py`:

```python
application.add_handler(CommandHandler("stars", h_int._make_runner("stars")))
```

That's it. The integration is auto-loaded at startup, listed by `/integrations`, and gets free retry/error handling from the framework.

---

## 🦾 Autonomy

`src/autonomy/` is the brain that runs *without* a user prompt.

```
┌──────────────────────┐
│   APScheduler loop   │
└──────────┬───────────┘
           │
   ┌───────┴────────────────────────────────────┐
   ▼                ▼                ▼          ▼
heartbeat_job   daily_fact_job   expiry_sweep   your_job
   (cron)        (cron)          (interval)     (any)
```

Default jobs:

- **`heartbeat`** — daily DM to the owner so you know it's alive.
- **`daily_fact`** — posts a random fun fact to `DAILY_FACT_CHANNEL` if set.
- **`expiry_sweep`** — every 6h, DMs users whose subscription ends in ≤3 days.

Add your own:

```python
# anywhere, after Application is built
from autonomy import scheduler

async def watch_btc(bot):
    # ...check price, alert if it crosses a threshold...

scheduler.add_interval("watch_btc", seconds=300, func=watch_btc, bot=app.bot)
scheduler.add_cron("morning_brief", "0 8 * * *", morning_brief, bot=app.bot)
```

Toggle the whole loop with `ENABLE_SCHEDULER=false`.

---

## 🏗️ Architecture

```
src/
├── bot.py                 # entry point — wires everything together
├── settings.py            # typed, validated env config
├── logging_setup.py       # JSON or human logs
├── safety.py              # @async_retry, @safe_handler
├── personality.py         # vibes, jokes, roasts, LLM hook
├── db.py                  # session_scope() + engine
├── models.py              # SQLAlchemy ORM (User, File, PromoCode, KV)
├── handlers/              # one module per concern
│   ├── core.py            #   /start /help /vibe /ping
│   ├── fun.py             #   /joke /roast /ask
│   ├── integrations_cmd.py#   /weather /price /fetch /scrape
│   ├── files.py admin.py …#   existing file-manager features
│   └── callbacks.py       #   inline keyboard router
├── integrations/          # plugins (auto-discovered)
│   ├── weather.py crypto.py jokes.py http_client.py
│   └── __init__.py        #   Integration base + registry
├── autonomy/
│   ├── scheduler.py       # APScheduler bootstrap
│   └── jobs.py            # default background jobs
└── utils/                 # permissions, keyboards, action group
```

Three runtime layers:

```
   ┌────────────────────────┐    ┌──────────────────────┐
   │    Telegram updates    │───▶│  CommandHandler /    │
   │  (polling or webhook)  │    │  CallbackQueryHandler│
   └────────────────────────┘    └──────────┬───────────┘
                                            ▼
   ┌────────────────────────┐    ┌──────────────────────┐
   │  APScheduler (cron +   │───▶│   Domain logic:      │
   │  intervals, autonomy)  │    │  personality, db,    │
   └────────────────────────┘    │  integrations        │
                                 └──────────┬───────────┘
                                            ▼
                                  ┌──────────────────────┐
                                  │  External world:     │
                                  │  REST APIs, scrape,  │
                                  │  SQLite / Postgres   │
                                  └──────────────────────┘
```

---

## 🔧 Configuration reference

All knobs live in `.env`. See [`.env.example`](./.env.example) for the full list. Highlights:

| Var | Default | Purpose |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | — (**required**) | From @BotFather |
| `BOT_OWNER_ID` | — (**required**) | Numeric Telegram id of the owner |
| `TELEGRAM_ACTION_GROUP_ID` | – | Group that receives renewal/feedback pings |
| `DATABASE_URL` | `sqlite:///bot.db` | SQLAlchemy URL |
| `DEFAULT_VIBE` | `funny` | `funny` / `pro` / `chill` |
| `LLM_PROVIDER` | – | Empty = offline banter only |
| `ENABLE_SCHEDULER` | `true` | Toggle background autonomy |
| `LOG_JSON` | `false` | Emit logs as JSON for aggregators |
| `RETRY_MAX_ATTEMPTS` | `5` | Network retry budget |

---

## 🧪 Tests & lint

```bash
make test         # pytest
make lint         # ruff check
make fmt          # ruff format
```

CI runs both on every push / PR — see `.github/workflows/ci.yml`.

---

## 🚢 Deploy

| Target | How |
|---|---|
| **Docker** | `docker compose up -d --build` |
| **Railway** | New project → deploy from repo → set env vars → it picks up the `Procfile` automatically |
| **Heroku** | `heroku create && git push heroku main && heroku ps:scale worker=1` |
| **Fly.io** | `fly launch` (use the included Dockerfile) |
| **Bare metal** | `python -m venv .venv && pip install -r requirements.txt && python src/bot.py` |

---

## 🔒 Security

- **Never** commit `.env`. The repo's `.gitignore` already covers it.
- The bot runs as a non-root user inside Docker.
- All HTTP calls go through `httpx` with a configurable timeout and retry budget.
- The previous version of this repo accidentally committed a `.env` with a live token — **rotate any token that was in `src/.env` before this commit**. Talk to @BotFather, run `/revoke` on the bot.

---

## 🤝 Contributing

PRs welcome. Please:

1. `make lint` and `make test` before pushing.
2. Add a test for new integrations.
3. Keep the funny tone, but no mean jokes.

---

## 📜 License

MIT. Be excellent to each other. 🫡
