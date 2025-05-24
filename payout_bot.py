import logging
import sys
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from config import PAYOUT_BOT_TOKEN, ADMIN_IDS, ERROR_INVALID_TOKEN
from database import get_db_connection, get_user
from localization import MESSAGES

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('payout_bot.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: CallbackContext):
    """Обработка команды /start для PayoutBot"""
    user_id = str(update.effective_user.id)
    username = update.effective_user.username or "User"
    await update.message.reply_text(
        MESSAGES['payout_welcome'].format(username=username),
        parse_mode='HTML'
    )

async def withdraw(update: Update, context: CallbackContext):
    """Обработка команды вывода средств"""
    user_id = str(update.effective_user.id)
    username = update.effective_user.username or "User"
    try:
        amount = float(context.args[0] if context.args else update.message.text.strip())
        if amount <= 0:
            await update.message.reply_text(MESSAGES['invalid_amount'], parse_mode='HTML')
            return
        user = get_user(user_id)
        if not user:
            await update.message.reply_text(MESSAGES['not_registered'], parse_mode='HTML')
            return
        if user[4]:  # is_blocked
            await update.message.reply_text(MESSAGES['user_blocked_message'], parse_mode='HTML')
            return
        if user[3] < amount:
            await update.message.reply_text(MESSAGES['insufficient_balance'], parse_mode='HTML')
            return
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO payouts (user_id, amount, status) VALUES (?, ?, ?)',
            (user_id, amount, 'pending')
        )
        cursor.execute(
            'UPDATE users SET balance = balance - ? WHERE user_id = ?',
            (amount, user_id)
        )
        conn.commit()
        payout_id = cursor.lastrowid
        for admin_id in ADMIN_IDS:
            await context.bot.send_message(
                chat_id=admin_id,
                text=MESSAGES['new_payout'].format(
                    payout_id=payout_id,
                    username=username,
                    user_id=user_id,
                    amount=amount
                ),
                parse_mode='HTML'
            )
        await update.message.reply_text(
            MESSAGES['payout_submitted'].format(payout_id=payout_id),
            parse_mode='HTML'
        )
    except (IndexError, ValueError):
        await update.message.reply_text(MESSAGES['withdraw_format'], parse_mode='HTML')
    except Exception as e:
        logger.error(f"Ошибка в withdraw: {e}")
        await update.message.reply_text(MESSAGES['error'], parse_mode='HTML')
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    """Запуск PayoutBot"""
    logger.info("Инициализация PayoutBot...")
    if not PAYOUT_BOT_TOKEN or PAYOUT_BOT_TOKEN == "your_payout_bot_token":
        logger.error(ERROR_INVALID_TOKEN)
        sys.exit(1)
    try:
        app = Application.builder().token(PAYOUT_BOT_TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("withdraw", withdraw))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, withdraw))
        logger.info("Запуск polling...")
        app.run_polling(allowed_updates=["message"])
    except Exception as e:
        logger.error(f"Ошибка при запуске PayoutBot: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()