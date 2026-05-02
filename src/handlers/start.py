"""Legacy /start handler kept for backwards compatibility.

New entry point is :func:`handlers.core.start_handler`.
"""
from __future__ import annotations

from .core import start_handler  # noqa: F401  (re-export)
