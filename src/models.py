"""SQLAlchemy ORM models."""
from __future__ import annotations

from sqlalchemy import Column, DateTime, Enum, Integer, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(String, unique=True, index=True)
    role = Column(Enum("admin", "premium", "group", "normal", name="user_roles"))
    category = Column(String)
    subscription_end = Column(DateTime)
    vibe = Column(String, default="funny")  # personality preference per user


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True)
    category = Column(String, index=True)
    file_id = Column(String, unique=True)
    uploaded_by = Column(String)
    upload_date = Column(DateTime)


class PromoCode(Base):
    __tablename__ = "promo_codes"

    code = Column(String, primary_key=True)
    validity_days = Column(Integer)
    created_by = Column(String)
    expiry_date = Column(DateTime)


class KV(Base):
    """Generic key-value store for autonomy bookkeeping (last heartbeat, etc.)."""

    __tablename__ = "kv"

    key = Column(String, primary_key=True)
    value = Column(Text)
    updated_at = Column(DateTime)
