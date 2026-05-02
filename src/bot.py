"""Bot entry point.

Wires together:
  • Configuration & structured logging
  • Database (with auto-migration via SQLAlchemy ``create_all``)
  • Command, callback, and message handlers
  • Pluggable integrations (auto-discovered)
  • Autonomous scheduler (APScheduler)

Run with:
    python -m bot              # from src/
    python src/bot.py          # from repo root
"""
from __future__ import annotations

import logging
import signal
import sys
from pathlib import Path

# Allow running both as ``python src/bot.py`` and ``python -m bot``.
SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from telegram import BotCommand, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

import integrations
from autonomy import jobs as autonomy_jobs
from autonomy import scheduler as autonomy_sched
from db import get_engine, session_scope
from handlers import (
    admin as h_admin,
)
from handlers import (
    callbacks as h_callbacks,
)
from handlers import (
    core as h_core,
)
from handlers import (
    files as h_files,
)
from handlers import (
    fun as h_fun,
)
from handlers import (
    group_user as h_group,
)
from handlers import (
    integrations_cmd as h_int,
)
from handlers import (
    normal_user as h_normal,
)
from handlers import (
    premium_user as h_premium,
)
from handlers import (
    subscription as h_sub,
)
from logging_setup import get_logger, setup_logging
from models import User
from settings import get_settings

logger = get_logger("telegramBot")


COMMANDS: list[BotCommand] = [
    BotCommand("start", "Register or refresh"),
    BotCommand("help", "Show command menu"),
    BotCommand("vibe", "Switch personality (funny/pro/chill)"),
    BotCommand("ping", "Health check"),
    BotCommand("joke", "Tell me a joke"),
    BotCommand("roast", "Roast me"),
    BotCommand("ask", "Ask me anything"),
    BotCommand("weather", "Current weather for a city"),
    BotCommand("price", "Crypto price"),
    BotCommand("fetch", "GET any URL"),
    BotCommand("scrape", "Extract text from a page"),
    BotCommand("integrations", "List available plugins"),
    BotCommand("files", "Browse files"),
    BotCommand("premium", "Premium menu"),
    BotCommand("group", "Group menu"),
    BotCommand("subscription", "View subscription"),
    BotCommand("renew", "Request renewal"),
    BotCommand("feedback", "Send feedback"),
    BotCommand("admin", "Admin panel"),
]


async def _ensure_owner(application: Application) -> None:
    settings = get_settings()
    with session_scope() as session:
        owner = session.query(User).filter_by(telegram_id=settings.bot_owner_id).first()
        if not owner:
            session.add(
                User(
                    telegram_id=settings.bot_owner_id,
                    role="admin",
                    vibe=settings.default_vibe,
                )
            )
            logger.info("Bootstrapped owner user (id=%s)", settings.bot_owner_id)


async def _post_init(application: Application) -> None:
    settings = get_settings()
    await _ensure_owner(application)

    try:
        await application.bot.set_my_commands(COMMANDS)
    except Exception:
        logger.exception("set_my_commands failed (non-fatal)")

    integrations.load_all()
    logger.info("Integrations loaded: %s", list(integrations.all_integrations()))

    if settings.enable_scheduler:
        autonomy_sched.add_cron(
            "heartbeat",
            settings.heartbeat_cron,
            autonomy_jobs.heartbeat_job,
            bot=application.bot,
        )
        autonomy_sched.add_cron(
            "daily_fact",
            settings.daily_fact_cron,
            autonomy_jobs.daily_fact_job,
            bot=application.bot,
        )
        autonomy_sched.add_interval(
            "expiry_sweep",
            seconds=6 * 3600,
            func=autonomy_jobs.expiry_sweep_job,
            bot=application.bot,
        )
        autonomy_sched.start()


async def _post_shutdown(application: Application) -> None:
    autonomy_sched.shutdown()


async def _error_handler(update: object, context) -> None:
    logger.exception(
        "Unhandled error while processing update: %s", getattr(context, "error", None)
    )


def build_application() -> Application:
    settings = get_settings()
    setup_logging(level=settings.log_level, json_output=settings.log_json)

    # Touch the engine so tables are created early and any DB error is loud.
    get_engine()

    application = (
        Application.builder()
        .token(settings.bot_token)
        .post_init(_post_init)
        .post_shutdown(_post_shutdown)
        .build()
    )

    # Core
    application.add_handler(CommandHandler("start", h_core.start_handler))
    application.add_handler(CommandHandler("help", h_core.help_handler))
    application.add_handler(CommandHandler("vibe", h_core.vibe_handler))
    application.add_handler(CommandHandler("ping", h_core.ping_handler))

    # Fun
    application.add_handler(CommandHandler("joke", h_fun.joke_handler))
    application.add_handler(CommandHandler("roast", h_fun.roast_handler))
    application.add_handler(CommandHandler("fact", h_fun.fact_handler))
    application.add_handler(CommandHandler("ask", h_fun.ask_handler))

    # Integrations
    application.add_handler(CommandHandler("integrations", h_int.list_handler))
    application.add_handler(CommandHandler("weather", h_int.weather_handler))
    application.add_handler(CommandHandler("price", h_int.price_handler))
    application.add_handler(CommandHandler("fetch", h_int.fetch_handler))
    application.add_handler(CommandHandler("scrape", h_int.scrape_handler))

    # File manager (existing)
    application.add_handler(CommandHandler("send_files", h_files.files_handler))
    application.add_handler(CommandHandler("files", h_normal.handle_normal_files))
    application.add_handler(CommandHandler("summary", h_group.handle_group_summary))
    application.add_handler(CommandHandler("premium", h_premium.handle_premium_files))
    application.add_handler(CommandHandler("subscription", h_premium.handle_subscription_summary))
    application.add_handler(CommandHandler("group", h_group.handle_group_files))
    application.add_handler(CommandHandler("renew", h_sub.request_renewal))
    application.add_handler(CommandHandler("feedback", h_sub.send_feedback))

    # Admin
    application.add_handler(CommandHandler("admin", h_admin.admin_handler))
    application.add_handler(CommandHandler("generate_promo", h_admin.generate_promo))

    # File uploads
    application.add_handler(MessageHandler(filters.Document.ALL, h_files.handle_file_upload))

    # Inline-keyboard router (last)
    application.add_handler(CallbackQueryHandler(h_callbacks.handle_callback_query))

    application.add_error_handler(_error_handler)
    return application


def main() -> None:
    application = build_application()

    logger.info("Bot started — polling for updates")

    # Run with built-in retry/backoff + clean shutdown on SIGINT/SIGTERM.
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        stop_signals=(signal.SIGINT, signal.SIGTERM, signal.SIGABRT),
        close_loop=False,
    )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logging.getLogger("telegramBot").exception("Fatal error during startup")
        # Exit non-zero so process supervisors restart us.
        sys.exit(1)
