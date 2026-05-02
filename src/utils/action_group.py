from __future__ import annotations

import logging

from telegram import Bot

from settings import get_settings

logger = logging.getLogger(__name__)


async def notify_action_group(
    bot: Bot,
    action_type: str,
    user_data: dict,
    details: str | None = None,
) -> None:
    """Send a structured notification to the configured action group."""
    settings = get_settings()
    chat_id = settings.action_group_id
    if not chat_id:
        logger.debug("No action group configured; skipping %s notification", action_type)
        return

    message = (
        f"🔔 New {action_type.upper()} Request\n\n"
        f"User: {user_data.get('name', '?')}\n"
        f"Profile: {user_data.get('profile_link', '?')}"
    )
    if details:
        message += f"\n\nDetails: {details}"

    try:
        await bot.send_message(chat_id=chat_id, text=message)
    except Exception:
        logger.exception("Failed to notify action group %s", chat_id)
