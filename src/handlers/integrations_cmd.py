"""Telegram commands that drive the pluggable integrations registry."""
from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

import integrations
from safety import safe_handler


def _get(name: str):
    return integrations.get(name)


@safe_handler
async def list_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    items = integrations.all_integrations()
    if not items:
        await update.message.reply_text("No integrations registered.")
        return
    lines = ["*Available integrations:*"]
    for name, plug in sorted(items.items()):
        lines.append(f"• `{plug.usage or '/' + name}` — {plug.description}")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


def _make_runner(name: str):
    @safe_handler
    async def runner(update: Update, context: ContextTypes.DEFAULT_TYPE):
        plug = _get(name)
        if plug is None:
            await update.message.reply_text(f"Integration '{name}' not loaded.")
            return
        await update.message.chat.send_action(action="typing")
        result = await plug.run(*(context.args or []))
        await update.message.reply_text(
            result.text,
            parse_mode="Markdown" if result.ok else None,
            disable_web_page_preview=True,
        )

    runner.__name__ = f"run_{name}"
    return runner


weather_handler = _make_runner("weather")
price_handler = _make_runner("price")
fetch_handler = _make_runner("fetch")
scrape_handler = _make_runner("scrape")
joke_online_handler = _make_runner("joke")
