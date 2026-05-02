from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from safety import safe_handler
from utils.action_group import notify_action_group


def _user_card(update: Update) -> dict:
    user = update.effective_user
    return {
        "name": f"{user.first_name} {user.last_name or ''}".strip(),
        "profile_link": f"tg://user?id={user.id}",
    }


@safe_handler
async def request_renewal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await notify_action_group(
        context.bot, "renewal", _user_card(update), "Subscription renewal requested"
    )
    await update.message.reply_text(
        "Your renewal request has been sent to our team — they'll process it shortly."
    )


@safe_handler
async def send_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args or []
    if not args:
        await update.message.reply_text(
            "Please provide feedback after the command.\nExample: /feedback your message here"
        )
        return
    await notify_action_group(
        context.bot, "feedback", _user_card(update), " ".join(args)
    )
    await update.message.reply_text("Thanks for the feedback — our team will review it.")
