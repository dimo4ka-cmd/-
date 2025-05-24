import logging
import sys
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from config import BOT_TOKEN, ERROR_INVALID_TOKEN
from handlers import start, admin_command, handle_message, handle_callback_query

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Запуск основного бота StarRentBot"""
    logger.info("Инициализация StarRentBot...")
    if not BOT_TOKEN or BOT_TOKEN == "your_bot_token":
        logger.error(ERROR_INVALID_TOKEN)
        sys.exit(1)

    try:
        app = Application.builder().token(BOT_TOKEN).build()

        # Команды
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("admin", admin_command))

        # Сообщения и кнопки
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        app.add_handler(CallbackQueryHandler(handle_callback_query))

        logger.info("Запуск polling...")
        app.run_polling(allowed_updates=["message", "callback_query"])
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()