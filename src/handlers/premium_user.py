from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import init_db, User, File
from datetime import datetime
from utils.permissions import check_user_access

async def handle_premium_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = init_db()
    user = session.query(User).filter_by(telegram_id=str(update.effective_user.id)).first()
    
    if user.role != 'premium':
        await update.message.reply_text("This feature is only available for premium users.")
        session.close()
        return
        
    keyboard = [
        [InlineKeyboardButton("TCP/Activator Files", callback_data="premium_tcp")],
        [InlineKeyboardButton("Unlimited Files", callback_data="premium_unlimited")],
        [InlineKeyboardButton("View Subscription", callback_data="premium_subscription")]
    ]
    
    await update.message.reply_text(
        "Premium Features:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    session.close()

async def handle_subscription_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = init_db()
    user = session.query(User).filter_by(telegram_id=str(update.effective_user.id)).first()
    
    if not user.subscription_end:
        await update.message.reply_text("No active subscription found.")
        session.close()
        return
        
    days_left = (user.subscription_end - datetime.now().date()).days
    await update.message.reply_text(
        f"Subscription Status:\n"
        f"Days remaining: {days_left}\n"
        f"Expires on: {user.subscription_end.strftime('%Y-%m-%d')}"
    )
    session.close()