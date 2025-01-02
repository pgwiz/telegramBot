import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from dotenv import load_dotenv
import os

# Import handlers
from handlers.start import start_handler
from handlers.files import files_handler, handle_file_upload
from handlers.admin import admin_handler, generate_promo
from handlers.premium_user import handle_premium_files, handle_subscription_summary
from handlers.group_user import handle_group_files, handle_group_summary
from handlers.normal_user import handle_normal_files, handle_normal_summary
from handlers.subscription import request_renewal, send_feedback
from handlers.callbacks import handle_callback_query

# Import utilities
from database import init_db
from utils.permissions import check_user_access

# Load environment variables
load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def error_handler(update, context):
    """Log errors caused by updates."""
    logger.error(f"Update {update} caused error {context.error}")

async def main():
    """Start the bot."""
    try:
        # Initialize database
        init_db()
        
        # Initialize bot
        application = Application.builder().token(TOKEN).build()
        
        # Basic command handlers
        application.add_handler(CommandHandler("start", start_handler))
        application.add_handler(CommandHandler("help", start_handler))
        
        # File management handlers
        application.add_handler(CommandHandler("send_files", files_handler))
        application.add_handler(CommandHandler("summary", handle_group_summary))
        
        # Admin handlers
        application.add_handler(CommandHandler("admin", admin_handler))
        application.add_handler(CommandHandler("generate_promo", generate_promo))
        
        # Premium user handlers
        application.add_handler(CommandHandler("premium", handle_premium_files))
        application.add_handler(CommandHandler("subscription", handle_subscription_summary))
        
        # Group user handlers
        application.add_handler(CommandHandler("group", handle_group_files))
        
        # Normal user handlers
        application.add_handler(CommandHandler("files", handle_normal_files))
        
        # Subscription and feedback handlers
        application.add_handler(CommandHandler("renew", request_renewal))
        application.add_handler(CommandHandler("feedback", send_feedback))
        
        # Callback query handler for inline buttons
        application.add_handler(CallbackQueryHandler(handle_callback_query))
        
        # Error handler
        application.add_error_handler(error_handler)
        
        # Start bot
        logger.info("Bot started successfully")
        await application.run_polling()
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        raise

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())