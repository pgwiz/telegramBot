from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.permissions import is_admin
from config import BOT_OWNER_ID
from database import init_db

async def handle_config(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle bot configuration commands for admin"""
    if not await is_admin(update.effective_user.id):
        await update.message.reply_text("⚠️ You don't have permission to access configuration settings.")
        return
        
    keyboard = [
        [InlineKeyboardButton("🔐 Security Settings", callback_data="config_security")],
        [InlineKeyboardButton("👥 Group Settings", callback_data="config_groups")],
        [InlineKeyboardButton("📊 Access Levels", callback_data="config_access")],
        [InlineKeyboardButton("⚙️ Bot Settings", callback_data="config_bot")]
    ]
    
    await update.message.reply_text(
        "🛠 *Bot Configuration Panel*\n"
        "Select a category to configure:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )