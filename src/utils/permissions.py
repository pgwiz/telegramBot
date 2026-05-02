from __future__ import annotations

from db import session_scope
from models import User
from settings import get_settings


async def is_admin(user_id: int | str) -> bool:
    settings = get_settings()
    if str(user_id) == settings.bot_owner_id:
        return True
    with session_scope() as session:
        user = session.query(User).filter_by(telegram_id=str(user_id)).first()
        return bool(user and user.role == "admin")


async def check_user_access(user: User) -> list[str]:
    if user.role == "admin":
        return ["all"]
    if user.role == "premium":
        return ["tcp", "unlimited"]
    if user.role == "group":
        return [user.category] if user.category else []
    return ["basic"]
