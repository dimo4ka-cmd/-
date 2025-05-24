# Конфигурация бота
BOT_TOKEN = "8092436444:AAElHAk3l13t1lRESckbWnbmBqz9P2GGVWg"  # Токен основного бота
PAYOUT_BOT_TOKEN = "your_payout_bot_token"  # Токен бота для выплат
DATABASE_PATH = "bot.db"  # Путь к базе данных
ADMIN_IDS = [7887610881]  # ID администраторов (замените)
REF_CODE = "ABC123"  # Дефолтный реферальный код
MAX_NUMBERS_PER_USER = 5  # Максимум номеров на пользователя

# Регулярные выражения
PHONE_REGEX = r'^7[0-9]{10}$'  # Формат номера: 79991234567
REF_CODE_REGEX = r'^[A-Z0-9]{6,10}$'  # Код: 6-10 букв/цифр

# Ошибки
ERROR_INVALID_TOKEN = "Ошибка: Неверный или отсутствующий токен бота."
ERROR_DATABASE = "Ошибка базы данных: {}"
