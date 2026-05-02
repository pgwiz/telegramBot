from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from db import session_scope
from models import File
from safety import safe_handler


@safe_handler
async def handle_normal_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Basic Files", callback_data="normal_basic")],
        [InlineKeyboardButton("View Summary", callback_data="normal_summary")],
    ]
    await update.message.reply_text(
        "Available Files:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


@safe_handler
async def handle_normal_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with session_scope() as session:
        basic_files = session.query(File).filter_by(category="basic").all()
        lines = ["Available basic files:", ""] + [f"- {f.file_id}" for f in basic_files]
    await update.message.reply_text("\n".join(lines) if basic_files else "No basic files yet.")
