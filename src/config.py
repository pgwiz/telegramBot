from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Bot configuration
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError('TELEGRAM_BOT_TOKEN is required')

# Admin configuration
BOT_OWNER_ID = os.getenv('BOT_OWNER_ID')
if not BOT_OWNER_ID:
    raise ValueError('BOT_OWNER_ID is required')

# Group configurations
ACTION_GROUP_ID = os.getenv('TELEGRAM_ACTION_GROUP_ID')
if not ACTION_GROUP_ID:
    raise ValueError('TELEGRAM_ACTION_GROUP_ID is required')

NORMAL_GROUP_ID = os.getenv('TELEGRAM_NORMAL_GROUP_ID')
if not NORMAL_GROUP_ID:
    raise ValueError('TELEGRAM_NORMAL_GROUP_ID is required')

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///bot.db')