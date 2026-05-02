from __future__ import annotations

from datetime import datetime, timedelta

from telegram import InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from db import session_scope
from models import PromoCode
from safety import safe_handler
from utils.keyboard import get_admin_keyboard
from utils.permissions import is_admin


@safe_handler
async def admin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update.effective_user.id):
        await update.message.reply_text("You don't have admin privileges.")
        return
    keyboard = await get_admin_keyboard()
    await update.message.reply_text(
        "Admin Panel — pick an action:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


@safe_handler
async def generate_promo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update.effective_user.id):
        return
    args = context.args or []
    if len(args) < 2:
        await update.message.reply_text("Usage: /generate_promo <label> <validity_days>")
        return

    label = args[0]
    try:
        validity_days = int(args[1])
    except ValueError:
        await update.message.reply_text("validity_days must be an integer.")
        return

    code = f"PROMO_{datetime.utcnow().strftime('%Y%m%d')}_{label}"
    expiry = datetime.utcnow() + timedelta(days=validity_days)
    with session_scope() as session:
        session.add(
            PromoCode(
                code=code,
                validity_days=validity_days,
                created_by=str(update.effective_user.id),
                expiry_date=expiry,
            )
        )
    await update.message.reply_text(f"Promo code generated: `{code}`", parse_mode="Markdown")
