from telegram import Update
from telegram.ext import ContextTypes
from database import init_db, User
from datetime import datetime

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = init_db()
    user_id = update.effective_user.id
    
    user = session.query(User).filter_by(telegram_id=str(user_id)).first()
    
    if not user:
        user = User(
            telegram_id=str(user_id),
            role='normal',
            subscription_end=None
        )
        session.add(user)
        session.commit()
        await update.message.reply_text("Welcome! You have basic access to files.")
    else:
        messages = {
            'admin': 'Welcome Admin! You have full access to manage files and users.',
            'premium': 'Welcome Premium User! You have unlimited access to all files.',
            'group': 'Welcome! You have access to your assigned category.',
            'normal': 'Welcome! You have basic access to files.'
        }
        await update.message.reply_text(messages.get(user.role, messages['normal']))
    
    session.close()