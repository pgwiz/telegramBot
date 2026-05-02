"""Core commands: /start, /help, /vibe, /ping."""
from __future__ import annotations

from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes

import personality
from db import session_scope
from models import User
from safety import safe_handler
from settings import get_settings

WELCOME = {
    "admin":   "Welcome Admin! Full power. Try /admin or /integrations.",
    "premium": "Welcome Premium User! Try /premium or /price btc.",
    "group":   "Welcome! Group access enabled. Try /group.",
    "normal":  "Welcome! Try /joke, /weather <city>, /price btc, or /help.",
}


HELP_TEXT = (
    "*Robot at your service.*\n\n"
    "*Core*\n"
    "  /start — register / refresh\n"
    "  /help — this menu\n"
    "  /vibe funny|pro|chill — change my mood\n"
    "  /ping — am I alive?\n\n"
    "*Fun*\n"
    "  /joke — dad joke\n"
    "  /roast — roast me\n"
    "  /ask <text> — ask me anything (LLM if configured)\n\n"
    "*Integrations*\n"
    "  /weather <city>\n"
    "  /price <symbol>\n"
    "  /fetch <url>\n"
    "  /scrape <url> [regex]\n"
    "  /integrations — list available plugins\n\n"
    "*File manager (existing)*\n"
    "  /files /premium /group /subscription /renew /feedback /admin"
)


@safe_handler
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    settings = get_settings()
    user_id = str(update.effective_user.id)
    with session_scope() as session:
        user = session.query(User).filter_by(telegram_id=user_id).first()
        if not user:
            role = "admin" if user_id == settings.bot_owner_id else "normal"
            user = User(telegram_id=user_id, role=role, vibe=settings.default_vibe)
            session.add(user)
            session.flush()
        role = user.role or "normal"
    text = personality.stylize(WELCOME.get(role, WELCOME["normal"]), settings.default_vibe)
    await update.message.reply_text(text)


@safe_handler
async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP_TEXT, parse_mode="Markdown")


@safe_handler
async def vibe_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args or []
    user_id = str(update.effective_user.id)
    if not args:
        with session_scope() as session:
            user = session.query(User).filter_by(telegram_id=user_id).first()
            current = (user.vibe if user else None) or get_settings().default_vibe
        await update.message.reply_text(
            f"Current vibe: *{current}*. Switch with /vibe funny|pro|chill",
            parse_mode="Markdown",
        )
        return

    new_vibe = args[0].lower()
    if new_vibe not in personality.VALID_VIBES:
        await update.message.reply_text("Pick one of: funny, pro, chill.")
        return

    with session_scope() as session:
        user = session.query(User).filter_by(telegram_id=user_id).first()
        if not user:
            user = User(telegram_id=user_id, role="normal", vibe=new_vibe)
            session.add(user)
        else:
            user.vibe = new_vibe

    await update.message.reply_text(personality.stylize(f"vibe set to {new_vibe}.", new_vibe))


@safe_handler
async def ping_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"pong 🏓 — {datetime.utcnow().isoformat()}Z")
