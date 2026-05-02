"""Inline-keyboard callback router."""
from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import ContextTypes

from db import session_scope
from models import User
from safety import safe_handler

logger = logging.getLogger(__name__)


async def _admin_files(query, context):
    await query.message.reply_text("Admin files management — coming soon.")


async def _admin_audit(query, context):
    await query.message.reply_text("User audit interface — coming soon.")


async def _premium_tcp(query, context):
    await query.message.reply_text("TCP/Activator files for premium users.")


async def _premium_unlimited(query, context):
    await query.message.reply_text("Unlimited files access.")


async def _group_tcp(query, context):
    await query.message.reply_text("TCP files for your group.")


async def _group_available(query, context):
    await query.message.reply_text("Available files for your group.")


async def _normal_basic(query, context):
    await query.message.reply_text("Basic files menu.")


async def _normal_summary(query, context):
    await query.message.reply_text("Summary of your basic files.")


_ROUTES = {
    ("admin", "files"): _admin_files,
    ("admin", "audit"): _admin_audit,
    ("premium", "tcp"): _premium_tcp,
    ("premium", "unlimited"): _premium_unlimited,
    ("group", "tcp"): _group_tcp,
    ("group", "available"): _group_available,
    ("normal", "basic"): _normal_basic,
    ("normal", "summary"): _normal_summary,
}


@safe_handler
async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Top-level inline-keyboard router. Format: ``<scope>_<action>[_...]``."""
    query = update.callback_query
    await query.answer()
    if not query.data:
        return

    parts = query.data.split("_")
    scope = parts[0] if parts else ""
    action = parts[1] if len(parts) > 1 else ""

    user_id = str(update.effective_user.id)
    with session_scope() as session:
        user = session.query(User).filter_by(telegram_id=user_id).first()
        role = user.role if user else "normal"

    if scope in {"admin", "premium", "group"} and role != scope and role != "admin":
        await query.message.reply_text("Unauthorized for this action.")
        return

    route = _ROUTES.get((scope, action))
    if route is None:
        logger.info("Unhandled callback: %s", query.data)
        await query.message.reply_text("That button isn't wired up yet.")
        return
    await route(query, context)
