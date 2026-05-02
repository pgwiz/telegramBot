"""Funny-dude commands: /joke /roast /ask /fact."""
from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

import personality
from db import session_scope
from models import User
from safety import safe_handler
from settings import get_settings


def _user_vibe(telegram_id: str) -> str:
    settings = get_settings()
    with session_scope() as session:
        user = session.query(User).filter_by(telegram_id=telegram_id).first()
        return (user.vibe if user and user.vibe else settings.default_vibe)


@safe_handler
async def joke_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(personality.joke())


@safe_handler
async def roast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(personality.roast())


@safe_handler
async def fact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🧠 {personality.fun_fact()}")


@safe_handler
async def ask_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args or []
    if not args:
        await update.message.reply_text("Usage: /ask <your question>")
        return
    prompt = " ".join(args)
    vibe = _user_vibe(str(update.effective_user.id))
    await update.message.chat.send_action(action="typing")
    answer = await personality.reply_to(prompt, vibe=vibe)
    await update.message.reply_text(answer)
