from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import init_db, User
from utils.action_group import notify_action_group

async def request_renewal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle subscription renewal requests"""
    user = update.effective_user
    user_data = {
        'name': f"{user.first_name} {user.last_name or ''}".strip(),
        'profile_link': f"tg://user?id={user.id}"
    }
    
    # Notify action group about renewal request
    await notify_action_group(
        context.bot,
        'renewal',
        user_data,
        "Subscription renewal requested"
    )
    
    await update.message.reply_text(
        "Your renewal request has been sent to our team. "
        "They will process it shortly."
    )

async def send_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user feedback"""
    user = update.effective_user
    feedback_text = ' '.join(context.args) if context.args else None
    
    if not feedback_text:
        await update.message.reply_text(
            "Please provide your feedback with the command.\n"
            "Example: /feedback Your message here"
        )
        return
        
    user_data = {
        'name': f"{user.first_name} {user.last_name or ''}".strip(),
        'profile_link': f"tg://user?id={user.id}"
    }
    
    # Notify action group about feedback
    await notify_action_group(
        context.bot,
        'feedback',
        user_data,
        feedback_text
    )
    
    await update.message.reply_text(
        "Thank you for your feedback! Our team will review it."
    )