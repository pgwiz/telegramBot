from database import init_db, User

async def is_admin(user_id: int) -> bool:
    session = init_db()
    user = session.query(User).filter_by(telegram_id=str(user_id)).first()
    is_admin = user and user.role == 'admin'
    session.close()
    return is_admin

async def check_user_access(user: User) -> list:
    if user.role == 'admin':
        return ['all']
    elif user.role == 'premium':
        return ['tcp', 'unlimited']
    elif user.role == 'group':
        return [user.category] if user.category else []
    else:
        return ['basic']