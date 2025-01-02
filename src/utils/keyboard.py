from telegram import InlineKeyboardButton

async def get_category_keyboard(categories: list) -> list:
    keyboard = []
    for category in categories:
        keyboard.append([
            InlineKeyboardButton(
                category.upper(), 
                callback_data=f"category_{category}"
            )
        ])
    return keyboard

async def get_admin_keyboard() -> list:
    return [
        [InlineKeyboardButton("Add/Update Files", callback_data="admin_files")],
        [InlineKeyboardButton("Delete Category", callback_data="admin_delete_category")],
        [InlineKeyboardButton("Audit Users", callback_data="admin_audit")],
        [InlineKeyboardButton("Generate Promo", callback_data="admin_promo")],
        [InlineKeyboardButton("View Logs", callback_data="admin_logs")]
    ]