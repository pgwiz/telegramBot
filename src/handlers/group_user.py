from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import init_db, User, File
from utils.permissions import check_user_access

async def handle_group_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = init_db()
    user = session.query(User).filter_by(telegram_id=str(update.effective_user.id)).first()
    
    if user.role != 'group':
        await update.message.reply_text("This feature is only available for group users.")
        session.close()
        return
        
    keyboard = [
        [InlineKeyboardButton("TCP/Activator Files", callback_data="group_tcp")],
        [InlineKeyboardButton("Available Files", callback_data="group_available")],
        [InlineKeyboardButton("View Summary", callback_data="group_summary")]
    ]
    
    await update.message.reply_text(
        f"Group Access - Category: {user.category}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    session.close()

async def handle_group_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = init_db()
    user = session.query(User).filter_by(telegram_id=str(update.effective_user.id)).first()
    
    files = session.query(File).filter_by(category=user.category).all()
    summary = f"Files in category {user.category}:\n\n"
    
    for file in files:
        summary += f"- {file.file_id} (Uploaded: {file.upload_date.strftime('%Y-%m-%d')})\n"
    
    await update.message.reply_text(summary)
    session.close()