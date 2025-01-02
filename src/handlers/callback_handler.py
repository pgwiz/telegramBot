# handlers/admin/callback_handler.py

from telegram import Update
from telegram.ext import CallbackContext
from .admin_handler import add_file, update_file, delete_file, delete_category, audit_user, view_logs
from .promo_handler import generate_promo

def handle_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    data = query.data

    if data == 'add_file':
        add_file(update, context)
    elif data == 'update_file':
        update_file(update, context)
    elif data == 'delete_file':
        delete_file(update, context)
    elif data == 'delete_category':
        delete_category(update, context)
    elif data == 'audit_user':
        audit_user(update, context)
    elif data == 'generate_promo':
        generate_promo(update, context)
    elif data == 'view_logs':
        view_logs(update, context)