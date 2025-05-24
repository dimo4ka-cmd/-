import re
from config import PHONE_REGEX, REF_CODE_REGEX, ADMIN_IDS
from database import get_user

def validate_phone(phone: str) -> bool:
    """Валидация номера телефона"""
    return bool(re.match(PHONE_REGEX, phone))

def validate_ref_code(code: str) -> bool:
    """Валидация реферального кода"""
    return bool(re.match(REF_CODE_REGEX, code))

def is_admin(user_id: str) -> bool:
    """Проверка, является ли пользователь админом"""
    return int(user_id) in ADMIN_IDS

def format_queue(queue: list, user_id: str, is_admin: bool = False) -> str:
    """Форматирование списка очереди для пользователей"""
    if not queue:
        return "📋 <b>Очередь пуста</b><br><br>Нажмите кнопку ниже, чтобы добавить номер 👇"
    text = "📋 <b>Ваша очередь</b><br><br>"
    for idx, q in enumerate(queue, 1):
        position = q[3]
        phone = q[2]
        if q[1] == user_id:
            text += f"📌 <b>{idx}. {phone}</b><br>   Позиция: <i>{position}</i><br><br>"
    if not any(q[1] == user_id for q in queue):
        text += "📭 У вас нет номеров в очереди.<br>"
    text += "Выберите действие ниже 👇"
    return text

def format_archive(archive: list) -> str:
    """Форматирование архива"""
    if not archive:
        return "🗄️ <b>Архив пуст</b><br><br>Ваш архив появится после завершения аренды 📌"
    text = "🗄️ <b>Ваш архив</b><br><br>"
    for idx, a in enumerate(archive, 1):
        text += f"📄 <b>{idx}. {a[0]}</b><br>   Статус: <i>{a[1]}</i><br>   Сумма: <i>${a[2]}</i><br><br>"
    text += "Нажмите кнопку ниже для продолжения 👇"
    return text

def format_stats(total_users: int, today_numbers: int) -> str:
    """Форматирование статистики"""
    return f"📊 <b>Статистика бота</b><br><br>👥 Пользователей: <i>{total_users}</i><br>📞 Сдано сегодня: <i>{today_numbers}</i><br><br>Выберите действие ниже 👇"