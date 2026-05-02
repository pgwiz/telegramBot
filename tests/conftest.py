"""Shared pytest fixtures."""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# Set required env vars before settings is imported anywhere.
os.environ.setdefault("TELEGRAM_BOT_TOKEN", "dummy:test")
os.environ.setdefault("BOT_OWNER_ID", "1")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("ENABLE_SCHEDULER", "false")
