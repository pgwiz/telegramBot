"""Default background jobs.

These run autonomously (no user input). They're defensive — any exception is
caught and logged so a flaky integration can't bring the bot down.
"""
from __future__ import annotations

import logging
from datetime import datetime

from telegram import Bot

import personality
from db import session_scope
from models import KV, User
from settings import get_settings

logger = logging.getLogger(__name__)


async def _safe(name: str, coro):
    try:
        await coro
    except Exception:
        logger.exception("Job '%s' failed", name)


async def heartbeat_job(bot: Bot) -> None:
    """Daily ping to the owner so they know the bot is alive."""
    settings = get_settings()
    text = (
        "🫀 Heartbeat — bot is alive and well.\n"
        f"Mood: *{settings.default_vibe}*\n"
        f"Tip: {personality.fun_fact()}"
    )
    try:
        await bot.send_message(chat_id=int(settings.bot_owner_id), text=text, parse_mode="Markdown")
        with session_scope() as s:
            s.merge(KV(key="last_heartbeat", value=datetime.utcnow().isoformat(), updated_at=datetime.utcnow()))
    except Exception:
        logger.exception("heartbeat failed")


async def daily_fact_job(bot: Bot) -> None:
    settings = get_settings()
    if not settings.daily_fact_channel:
        return
    try:
        await bot.send_message(
            chat_id=settings.daily_fact_channel,
            text=f"🧠 Daily fact: {personality.fun_fact()}",
        )
    except Exception:
        logger.exception("daily fact post failed")


async def expiry_sweep_job(bot: Bot) -> None:
    """Notify users whose subscription is about to expire (within 3 days)."""
    settings = get_settings()
    today = datetime.utcnow().date()
    try:
        with session_scope() as session:
            users = session.query(User).filter(User.subscription_end.isnot(None)).all()
            for user in users:
                if user.subscription_end is None:
                    continue
                end_date = user.subscription_end.date() if hasattr(user.subscription_end, "date") else user.subscription_end
                days_left = (end_date - today).days
                if 0 <= days_left <= 3:
                    try:
                        await bot.send_message(
                            chat_id=int(user.telegram_id),
                            text=(
                                f"⏰ Heads up — your subscription expires in {days_left} day(s).\n"
                                f"Renew with /renew."
                            ),
                        )
                    except Exception:
                        logger.warning("Could not DM user %s", user.telegram_id)
    except Exception:
        logger.exception("expiry sweep failed")
    finally:
        # Touch KV regardless so we have a freshness signal.
        try:
            with session_scope() as s:
                s.merge(KV(key="last_expiry_sweep", value=datetime.utcnow().isoformat(), updated_at=datetime.utcnow()))
        except Exception:
            pass
        # silence the unused arg warning when scheduler is disabled
        _ = settings
