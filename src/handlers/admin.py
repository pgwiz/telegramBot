from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import init_db, User, PromoCode
from datetime import datetime, timedelta
from utils.permissions import is_admin
from utils.keyboard import get_admin_keyboard

async def admin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update.effective_user.id):
        await update.message.reply_text("You don't have admin privileges.")
        return
    
    keyboard = await get_admin_keyboard()
    await update.message.reply_text(
        "Admin Panel - Select an action:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def generate_promo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update.effective_user.id):
        return
        
    session = init_db()
    code = f"PROMO_{datetime.now().strftime('%Y%m%d')}_{context.args[0]}"
    validity_days = int(context.args[1])
    
    promo = PromoCode(
        code=code,
        validity_days=validity_days,
        created_by=str(update.effective_user.id),
        expiry_date=datetime.now() + timedelta(days=validity_days)
    )
    
    session.add(promo)
    session.commit()
    session.close()
    
    await update.message.reply_text(f"Promo code generated: {code}")