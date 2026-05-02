from __future__ import annotations

from datetime import datetime

from telegram import InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from db import session_scope
from models import File, User
from safety import safe_handler
from utils.keyboard import get_category_keyboard
from utils.permissions import check_user_access


@safe_handler
async def files_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    with session_scope() as session:
        user = session.query(User).filter_by(telegram_id=user_id).first()
        if not user:
            await update.message.reply_text("Please start the bot first with /start")
            return
        categories = await check_user_access(user)

    keyboard = await get_category_keyboard(categories)
    await update.message.reply_text(
        "Select a category:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


@safe_handler
async def handle_file_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not getattr(update.message, "document", None):
        await update.message.reply_text("Please send a file.")
        return

    file_id = update.message.document.file_id
    category = context.user_data.get("current_category") if context.user_data else None
    user_id = str(update.effective_user.id)

    with session_scope() as session:
        session.add(
            File(
                category=category,
                file_id=file_id,
                uploaded_by=user_id,
                upload_date=datetime.utcnow(),
            )
        )
    await update.message.reply_text("File uploaded successfully!")
