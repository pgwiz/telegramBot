"""Backward-compat shim. New code uses :mod:`settings`."""
from __future__ import annotations

from settings import get_settings

_settings = get_settings()
BOT_TOKEN = _settings.bot_token
BOT_OWNER_ID = _settings.bot_owner_id
ACTION_GROUP_ID = _settings.action_group_id
NORMAL_GROUP_ID = _settings.normal_group_id
DATABASE_URL = _settings.database_url
