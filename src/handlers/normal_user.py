from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import init_db, User, File

async def handle_normal_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = init_db()
    user = session.query(User).filter_by(telegram_id=str(update.effective_user.id)).first()
    
    keyboard = [
        [InlineKeyboardButton("Basic Files", callback_data="normal_basic")],
        [InlineKeyboardButton("View Summary", callback_data="normal_summary")]
    ]
    
    await update.message.reply_text(
        "Available Files:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    session.close()

async def handle_normal_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = init_db()
    basic_files = session.query(File).filter_by(category='basic').all()
    
    summary = "Available basic files:\n\n"
    for file in basic_files:
        summary += f"- {file.file_id}\n"
    
    await update.message.reply_text(summary)
    session.close()