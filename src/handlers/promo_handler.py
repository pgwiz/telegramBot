# handlers/admin/promo_handler.py

import random
import string
from telegram import Update
from telegram.ext import CallbackContext

def generate_promo(update: Update, context: CallbackContext):
    # Generate an 8-character alphanumeric promo code
    promo_code = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    
    # Check if the validity period is provided
    if context.args:
        validity_period = ' '.join(context.args)
    else:
        validity_period = "30 days"  # Default validity period
    
    update.callback_query.message.reply_text(f"Promo Code: {promo_code}\nValidity: {validity_period}")