"""Centralized configuration loaded from environment variables.

All runtime knobs live here so the rest of the codebase never reads ``os.environ``
directly. Validation happens once at import time and produces clear errors.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv


def _find_env_file() -> Path | None:
    here = Path(__file__).resolve()
    for parent in (here.parent, *here.parents):
        candidate = parent / ".env"
        if candidate.is_file():
            return candidate
    return None


_env_path = _find_env_file()
if _env_path is not None:
    load_dotenv(_env_path)
else:
    load_dotenv()


def _bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on", "y"}


def _int(value: str | None, default: int) -> int:
    try:
        return int(value) if value not in (None, "") else default
    except ValueError:
        return default


def _float(value: str | None, default: float) -> float:
    try:
        return float(value) if value not in (None, "") else default
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    """Immutable, fully-typed configuration."""

    # Telegram
    bot_token: str
    bot_owner_id: str
    action_group_id: str | None
    normal_group_id: str | None

    # Database
    database_url: str = "sqlite:///bot.db"

    # Personality
    default_vibe: str = "funny"
    llm_provider: str = ""
    llm_api_key: str = ""
    llm_model: str = "gpt-4o-mini"
    llm_base_url: str = ""

    # Autonomy
    enable_scheduler: bool = True
    heartbeat_cron: str = "0 9 * * *"
    daily_fact_channel: str = ""
    daily_fact_cron: str = "0 12 * * *"

    # Robustness
    log_level: str = "INFO"
    log_json: bool = False
    http_timeout: float = 15.0
    retry_max_attempts: int = 5
    retry_backoff_base: float = 1.5

    # Integrations
    openweather_api_key: str = ""
    coingecko_base: str = "https://api.coingecko.com/api/v3"

    # Misc
    extras: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_env(cls) -> Settings:
        token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        if not token:
            raise RuntimeError(
                "TELEGRAM_BOT_TOKEN is required. Copy .env.example to .env and fill it in."
            )
        owner = os.getenv("BOT_OWNER_ID", "").strip()
        if not owner:
            raise RuntimeError("BOT_OWNER_ID is required.")

        return cls(
            bot_token=token,
            bot_owner_id=owner,
            action_group_id=os.getenv("TELEGRAM_ACTION_GROUP_ID") or None,
            normal_group_id=os.getenv("TELEGRAM_NORMAL_GROUP_ID") or None,
            database_url=os.getenv("DATABASE_URL", "sqlite:///bot.db"),
            default_vibe=os.getenv("DEFAULT_VIBE", "funny").lower(),
            llm_provider=os.getenv("LLM_PROVIDER", "").lower(),
            llm_api_key=os.getenv("LLM_API_KEY", ""),
            llm_model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
            llm_base_url=os.getenv("LLM_BASE_URL", ""),
            enable_scheduler=_bool(os.getenv("ENABLE_SCHEDULER"), True),
            heartbeat_cron=os.getenv("HEARTBEAT_CRON", "0 9 * * *"),
            daily_fact_channel=os.getenv("DAILY_FACT_CHANNEL", ""),
            daily_fact_cron=os.getenv("DAILY_FACT_CRON", "0 12 * * *"),
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
            log_json=_bool(os.getenv("LOG_JSON"), False),
            http_timeout=_float(os.getenv("HTTP_TIMEOUT"), 15.0),
            retry_max_attempts=_int(os.getenv("RETRY_MAX_ATTEMPTS"), 5),
            retry_backoff_base=_float(os.getenv("RETRY_BACKOFF_BASE"), 1.5),
            openweather_api_key=os.getenv("OPENWEATHER_API_KEY", ""),
            coingecko_base=os.getenv(
                "COINGECKO_BASE", "https://api.coingecko.com/api/v3"
            ),
        )


_settings: Settings | None = None


def get_settings() -> Settings:
    """Return a process-wide :class:`Settings` instance (lazy)."""
    global _settings
    if _settings is None:
        _settings = Settings.from_env()
    return _settings
