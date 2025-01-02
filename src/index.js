require('dotenv').config();
const TelegramBot = require('node-telegram-bot-api');
const { setupDatabase } = require('./database');
const { handleStart } = require('./handlers/startHandler');
const { handleFiles } = require('./handlers/fileHandler');
const { handleAdmin } = require('./handlers/adminHandler');
const { logger } = require('./utils/logger');

const token = process.env.TELEGRAM_BOT_TOKEN;
if (!token) {
  logger.error('TELEGRAM_BOT_TOKEN is required');
  process.exit(1);
}

const bot = new TelegramBot(token, { polling: true });

// Initialize database
setupDatabase();

// Command handlers
bot.onText(/\/start/, handleStart);
bot.onText(/\/send_files/, handleFiles);
bot.onText(/\/admin/, handleAdmin);

// Error handling
bot.on('polling_error', (error) => {
  logger.error('Polling error:', error);
});

logger.info('Bot started successfully');