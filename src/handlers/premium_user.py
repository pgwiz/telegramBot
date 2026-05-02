from __future__ import annotations

from datetime import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from db import session_scope
from models import User
from safety import safe_handler


@safe_handler
async def handle_premium_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    with session_scope() as session:
        user = session.query(User).filter_by(telegram_id=user_id).first()
        if not user or user.role != "premium":
            await update.message.reply_text("This feature is only available for premium users.")
            return
    keyboard = [
        [InlineKeyboardButton("TCP/Activator Files", callback_data="premium_tcp")],
        [InlineKeyboardButton("Unlimited Files", callback_data="premium_unlimited")],
        [InlineKeyboardButton("View Subscription", callback_data="premium_subscription")],
    ]
    await update.message.reply_text("Premium Features:", reply_markup=InlineKeyboardMarkup(keyboard))


@safe_handler
async def handle_subscription_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    with session_scope() as session:
        user = session.query(User).filter_by(telegram_id=user_id).first()
        if not user or not user.subscription_end:
            await update.message.reply_text("No active subscription found.")
            return
        end = user.subscription_end
        if hasattr(end, "date"):
            end_date = end.date()
        else:
            end_date = end
        days_left = (end_date - datetime.utcnow().date()).days

    await update.message.reply_text(
        f"Subscription Status:\n"
        f"Days remaining: {days_left}\n"
        f"Expires on: {end_date.strftime('%Y-%m-%d')}"
    )
