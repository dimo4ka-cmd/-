from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from database import get_user

ITEMS_PER_PAGE = 5

def get_user_menu():
    """Пользовательское меню"""
    keyboard = [
        [
            InlineKeyboardButton("📋 Моя очередь", callback_data="action:queue"),
            InlineKeyboardButton("💸 Баланс", callback_data="action:payout")
        ],
        [
            InlineKeyboardButton("➕ Новый номер", callback_data="action:add_phone"),
            InlineKeyboardButton("📩 Поддержка", callback_data="action:support")
        ],
        [
            InlineKeyboardButton("🗄️ Архив", callback_data="action:archive"),
            InlineKeyboardButton("📊 Статистика", callback_data="action:stats")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_menu():
    """Админ-меню"""
    keyboard = [
        [
            InlineKeyboardButton("📋 Очередь", callback_data="action:queue:1"),
            InlineKeyboardButton("📝 Заявки", callback_data="action:requests:1")
        ],
        [
            InlineKeyboardButton("💸 Выплаты", callback_data="action:payouts"),
            InlineKeyboardButton("📩 Тикеты", callback_data="action:tickets:1")
        ],
        [
            InlineKeyboardButton("🔑 Коды", callback_data="action:codes"),
            InlineKeyboardButton("🚫 Блокировки", callback_data="action:block")
        ],
        [
            InlineKeyboardButton("💰 Изменить баланс", callback_data="action:balance"),
            InlineKeyboardButton("📈 Админ-статистика", callback_data="action:admin_stats")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_ref_code_menu():
    """Меню реферального кода"""
    keyboard = [
        [InlineKeyboardButton("🔑 Ввести код ABC123", callback_data="ref_code:ABC123")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_action_menu(action_type: str):
    """Меню админ-действий"""
    keyboard = []
    if action_type == 'codes':
        keyboard.append([InlineKeyboardButton("➕ Создать код", callback_data="action:create_code")])
    elif action_type == 'queue':
        keyboard.append([InlineKeyboardButton("📤 В архив", callback_data="action:move_archive")])
    elif action_type == 'payouts':
        keyboard.append([InlineKeyboardButton("🔄 Обновить выплату", callback_data="action:update_payout")])
    elif action_type == 'tickets':
        keyboard.append([InlineKeyboardButton("💬 Ответить на тикет", callback_data="action:respond_ticket")])
    keyboard.append([InlineKeyboardButton("🔄 Обновить список", callback_data=f"action:{action_type}:1")])
    keyboard.append([InlineKeyboardButton("⬅️ В меню", callback_data="action:back")])
    return InlineKeyboardMarkup(keyboard)

def get_paginated_requests(requests: list, page: int) -> tuple:
    """Пагинация заявок"""
    total = len(requests)
    start = (page - 1) * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    paginated = requests[start:end]
    
    text = f"📝 <b>Заявки на аренду</b> (Страница {page}/{max(1, (total + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE)})<br><br>" if paginated else "📝 <b>Нет заявок на аренду</b>"
    keyboard = []
    
    for r in paginated:
        user_info = get_user(r[1])
        username = user_info['username'] if user_info else "unknown"
        text += f"📋 <b>ID: {r[0]}</b><br>   Пользователь: <i>@{username} ({r[1]})</i><br>   Номер: <i>{r[2]}</i><br>   Статус: <i>{r[3]}</i><br>   Дата: <i>{r[4]}</i><br><br>"
        if r[3] == 'pending':
            keyboard.append([
                InlineKeyboardButton("✅ Одобрить", callback_data=f"action:approve_request:{r[0]}"),
                InlineKeyboardButton("❌ Отклонить", callback_data=f"action:reject_request:{r[0]}")
            ])
    
    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"action:requests:{page-1}"))
    if end < total:
        nav_buttons.append(InlineKeyboardButton("Вперёд ➡️", callback_data=f"action:requests:{page+1}"))
    if nav_buttons:
        keyboard.append(nav_buttons)
    keyboard.append([InlineKeyboardButton("⬅️ В меню", callback_data="action:back")])
    
    return text, InlineKeyboardMarkup(keyboard)

def get_paginated_queue(queue: list, page: int, user_id: str, is_admin: bool = False) -> tuple:
    """Пагинация очереди"""
    total = len(queue)
    start = (page - 1) * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    paginated = queue[start:end]
    
    text = f"📋 <b>Очередь</b> (Страница {page}/{max(1, (total + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE)})<br><br>" if paginated else "📋 <b>Очередь пуста</b>"
    keyboard = []
    
    for idx, q in enumerate(paginated, start + 1):
        position = q[3]
        phone = q[2]
        user_info = get_user(q[1])
        username = user_info['username'] if user_info else "unknown"
        if is_admin:
            text += f"📌 <b>{idx}. ID: {q[0]}</b><br>   Пользователь: <i>@{username} ({q[1]})</i><br>   Номер: <i>{phone}</i><br>   Позиция: <i>{position}</i><br><br>"
        else:
            if q[1] == user_id:
                text += f"📌 <b>{idx}. {phone}</b><br>   Позиция: <i>{position}</i><br><br>"
    
    if not is_admin and not any(q[1] == user_id for q in queue):
        text += "📭 У вас нет номеров в очереди.<br>"
    
    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"action:queue:{page-1}"))
    if end < total:
        nav_buttons.append(InlineKeyboardButton("Вперёд ➡️", callback_data=f"action:queue:{page+1}"))
    if nav_buttons:
        keyboard.append(nav_buttons)
    keyboard.append([InlineKeyboardButton("⬅️ В меню", callback_data="action:back")])
    
    return text, InlineKeyboardMarkup(keyboard)

def get_paginated_tickets(tickets: list, page: int) -> tuple:
    """Пагинация тикетов"""
    total = len(tickets)
    start = (page - 1) * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    paginated = tickets[start:end]
    
    text = f"📩 <b>Тикеты</b> (Страница {page}/{max(1, (total + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE)})<br><br>" if paginated else "📩 <b>Нет тикетов</b>"
    keyboard = []
    
    for t in paginated:
        user_info = get_user(t[1])
        username = user_info['username'] if user_info else "unknown"
        text += f"📬 <b>ID: {t[0]}</b><br>   Пользователь: <i>@{username} ({t[1]})</i><br>   Вопрос: <i>{t[2][:50]}{'...' if len(t[2]) > 50 else ''}</i><br>   Статус: <i>{t[4]}</i><br>   Дата: <i>{t[5]}</i><br><br>"
    
    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"action:tickets:{page-1}"))
    if end < total:
        nav_buttons.append(InlineKeyboardButton("Вперёд ➡️", callback_data=f"action:tickets:{page+1}"))
    if nav_buttons:
        keyboard.append(nav_buttons)
    keyboard.append([InlineKeyboardButton("⬅️ В меню", callback_data="action:back")])
    
    return text, InlineKeyboardMarkup(keyboard)