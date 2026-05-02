from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from db import session_scope
from models import File, User
from safety import safe_handler


@safe_handler
async def handle_group_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    with session_scope() as session:
        user = session.query(User).filter_by(telegram_id=user_id).first()
        if not user or user.role != "group":
            await update.message.reply_text("This feature is only available for group users.")
            return
        category = user.category

    keyboard = [
        [InlineKeyboardButton("TCP/Activator Files", callback_data="group_tcp")],
        [InlineKeyboardButton("Available Files", callback_data="group_available")],
        [InlineKeyboardButton("View Summary", callback_data="group_summary")],
    ]
    await update.message.reply_text(
        f"Group Access — Category: {category}",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


@safe_handler
async def handle_group_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    with session_scope() as session:
        user = session.query(User).filter_by(telegram_id=user_id).first()
        if not user:
            await update.message.reply_text("Run /start first.")
            return
        files = session.query(File).filter_by(category=user.category).all()
        lines = [f"Files in category {user.category}:", ""]
        for f in files:
            date_str = f.upload_date.strftime("%Y-%m-%d") if f.upload_date else "n/a"
            lines.append(f"- {f.file_id} (Uploaded: {date_str})")

    await update.message.reply_text("\n".join(lines) if files else f"No files in category {user.category}.")
