"""Backward-compat shim. New code should import from :mod:`db` and :mod:`models`."""
from __future__ import annotations

from db import init_db, session_scope  # noqa: F401  (re-export)
from models import KV, Base, File, PromoCode, User  # noqa: F401  (re-export)
