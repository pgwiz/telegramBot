"""Database session helper smoke tests."""
from __future__ import annotations

import pytest

from db import get_engine, session_scope
from models import User


def test_engine_lazy_init():
    engine = get_engine()
    assert engine is not None


def test_session_scope_commit():
    with session_scope() as session:
        session.add(User(telegram_id="999", role="normal", vibe="funny"))
    with session_scope() as session:
        u = session.query(User).filter_by(telegram_id="999").first()
        assert u is not None
        assert u.role == "normal"


def test_session_scope_rollback_on_error():
    with pytest.raises(RuntimeError):
        with session_scope() as session:
            session.add(User(telegram_id="998", role="normal", vibe="funny"))
            raise RuntimeError("boom")
    with session_scope() as session:
        assert session.query(User).filter_by(telegram_id="998").first() is None
