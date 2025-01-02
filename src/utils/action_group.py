from telegram import Bot
from database import init_db, User
import os

ACTION_GROUP_ID = os.getenv('TELEGRAM_ACTION_GROUP_ID')

async def notify_action_group(bot: Bot, action_type: str, user_data: dict, details: str = None):
    """Send notifications to action group for user actions"""
    if not ACTION_GROUP_ID:
        return
        
    message = (
        f"🔔 New {action_type.upper()} Request\n\n"
        f"User: {user_data['name']}\n"
        f"Profile: {user_data['profile_link']}\n"
    )
    
    if details:
        message += f"\nDetails: {details}"
        
    await bot.send_message(chat_id=ACTION_GROUP_ID, text=message)