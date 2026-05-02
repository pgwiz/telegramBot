"""Database engine, session factory, and a context-managed session helper.

This module replaces the old ``init_db()`` pattern that created a new engine on
every call (and leaked sessions). The engine is built once; callers use the
:func:`session_scope` context manager.
"""
from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from models import Base
from settings import get_settings

_engine = None
_SessionFactory: sessionmaker | None = None


def _build_engine():
    settings = get_settings()
    kwargs: dict = {"future": True}
    if settings.database_url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
    return create_engine(settings.database_url, **kwargs)


def get_engine():
    global _engine
    if _engine is None:
        _engine = _build_engine()
        Base.metadata.create_all(_engine)
    return _engine


def get_session_factory() -> sessionmaker:
    global _SessionFactory
    if _SessionFactory is None:
        _SessionFactory = sessionmaker(bind=get_engine(), expire_on_commit=False, future=True)
    return _SessionFactory


@contextmanager
def session_scope() -> Iterator[Session]:
    """Yield a session, commit on success, rollback on error, always close."""
    session = get_session_factory()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# --- Backwards compatibility shim ---
def init_db() -> Session:
    """Legacy helper retained so existing handlers keep working.

    New code should use :func:`session_scope` instead.
    """
    return get_session_factory()()
