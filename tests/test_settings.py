"""Settings module loads from env without raising."""
from __future__ import annotations

from settings import Settings, get_settings


def test_settings_load():
    s = get_settings()
    assert isinstance(s, Settings)
    assert s.bot_token
    assert s.bot_owner_id
    assert s.default_vibe in ("funny", "pro", "chill")


def test_settings_defaults():
    s = get_settings()
    assert s.retry_max_attempts >= 1
    assert s.http_timeout > 0
