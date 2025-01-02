from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import init_db, User, File
from datetime import datetime
from utils.permissions import check_user_access
from utils.keyboard import get_category_keyboard

async def files_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = init_db()
    user_id = update.effective_user.id
    user = session.query(User).filter_by(telegram_id=str(user_id)).first()
    
    if not user:
        await update.message.reply_text("Please start the bot first with /start")
        session.close()
        return
        
    categories = await check_user_access(user)
    keyboard = await get_category_keyboard(categories)
    
    await update.message.reply_text(
        "Select a category:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    session.close()

async def handle_file_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = init_db()
    user_id = update.effective_user.id
    
    if not hasattr(update.message, 'document'):
        await update.message.reply_text("Please send a file.")
        session.close()
        return
        
    file_id = update.message.document.file_id
    category = context.user_data.get('current_category')
    
    new_file = File(
        category=category,
        file_id=file_id,
        uploaded_by=str(user_id),
        upload_date=datetime.now()
    )
    
    session.add(new_file)
    session.commit()
    session.close()
    
    await update.message.reply_text("File uploaded successfully!")