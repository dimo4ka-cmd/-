MESSAGES = {
    'welcome': "👋 <b>Привет, @{username}!</b><br>Добро пожаловать в <b>StarRentBot</b>! 🚀<br><br>Введите реферальный код, чтобы начать 👇",
    'already_registered': "🎉 <b>С возвращением, @{username}!</b><br>Вы уже с нами! 😎<br><br>Выберите действие 👇",
    'enter_ref_code': "🔑 <b>Привет, @{username}!</b><br>Введите реферальный код для регистрации 👇",
    'access_denied': "🚫 <b>Доступ запрещён</b><br>Эта команда только для админов 👮",
    'user_blocked_message': "🚫 <b>Ваш аккаунт заблокирован</b><br>Обратитесь в поддержку 📩",
    'unknown_command': "❓ <b>Ой, что-то пошло не так</b><br>Используйте кнопки ниже 👇",
    'admin_unknown_command': "❓ <b>Неизвестная команда</b><br>Админам доступны только кнопки ниже 👇",
    'admin_panel': "🛠️ <b>Админ-панель, @{username}!</b><br><br>Управляйте ботом с помощью кнопок 👇",
    'codes_title': "🔑 <b>Реферальные коды</b>",
    'no_codes': "🔑 <b>Нет активных кодов</b><br>Создайте новый код с помощью кнопки 👇",
    'create_code_prompt': "➕ <b>Создать код</b><br><br>Введите: <code>&lt;код&gt; &lt;макс_использований&gt;</code><br><i>Пример</i>: <code>CODE2025 2</code><br>",
    'create_code_format': "❌ <b>Ошибка формата</b><br>Используйте: <code>&lt;код&gt; &lt;макс_использований&gt;</code>",
    'code_created': "✅ <b>Код успешно создан</b>: <i>{code}</i>",
    'move_archive_prompt': "📤 <b>Переместить в архив</b><br><br>Введите: <code>&lt;ID_очереди&gt; &lt;статус&gt; &lt;сумма&gt;</code><br><i>Пример</i>: <code>1 approved 10.0</code><br>",
    'move_archive_format': "❌ <b>Ошибка формата</b><br>Используйте: <code>&lt;ID_очереди&gt; &lt;статус&gt; &lt;сумма&gt;</code>",
    'moved_to_archive': "✅ <b>Успешно перемещено в архив</b> 🎉",
    'payouts_title': "💸 <b>Заявки на выплаты</b>",
    'no_payouts': "💸 <b>Нет заявок на выплаты</b><br>Обновите или вернитесь в меню 👇",
    'update_payout_prompt': "🔄 <b>Обновить выплату</b><br><br>Введите: <code>&lt;ID_выплаты&gt; &lt;статус&gt;</code><br><i>Пример</i>: <code>1 approved</code><br>",
    'update_payout_format': "❌ <b>Ошибка формата</b><br>Используйте: <code>&lt;ID_выплаты&gt; &lt;статус&gt;</code>",
    'payout_updated': "✅ <b>Выплата обновлена</b>: <i>{payout_id}</i>",
    'tickets_title': "📩 <b>Тикеты поддержки</b>",
    'no_tickets': "📩 <b>Нет активных тикетов</b><br>Обновите или вернитесь в меню 👇",
    'respond_ticket_prompt': "💬 <b>Ответить на тикет</b><br><br>Введите: <code>&lt;ID_тикета&gt; &lt;ответ&gt;</code><br><i>Пример</i>: <code>1 Ваш вопрос решён</code><br>",
    'respond_ticket_format': "❌ <b>Ошибка формата</b><br>Используйте: <code>&lt;ID_тикета&gt; &lt;ответ&gt;</code>",
    'ticket_responded': "✅ <b>Ответ отправлен на тикет</b>: <i>{ticket_id}</i>",
    'ticket_response': "📬 <b>Ответ на тикет #{ticket_id}</b><br><br>{response}<br><br>Свяжитесь снова, если нужно! 👇",
    'new_support_ticket': "📩 <b>Новый тикет #{ticket_id}</b><br><br>👤 Пользователь: <i>@{username} ({user_id})</i><br>❓ Вопрос: <i>{question}</i><br>🕒 Дата: <i>{timestamp}</i><br><br>Ответьте через админ-панель 👇",
    'support_prompt': "📩 <b>Задайте вопрос поддержке</b><br><br>Опишите проблему (мин. 5 символов):<br>",
    'support_too_short': "❌ <b>Слишком коротко</b><br>Вопрос должен быть не менее 5 символов 📝",
    'support_submitted': "✅ <b>Тикет #{ticket_id} отправлен!</b><br>Мы ответим скоро 📬",
    'new_rent_request': "📝 <b>Новая заявка #{request_id}</b><br><br>👤 Пользователь: <i>@{username} ({user_id})</i><br>📞 Номер: <i>{phone_number}</i><br>🕒 Дата: <i>{timestamp}</i><br><br>Одобрите или отклоните в админ-панели 👇",
    'request_approved': "✅ <b>Заявка на номер {phone_number} одобрена!</b><br>Спасибо за участие 🎉",
    'request_approved_admin': "✅ <b>Заявка #{request_id} одобрена</b>",
    'request_rejected': "❌ <b>Заявка на номер {phone_number} отклонена</b><br>Попробуйте другой номер 📞",
    'request_rejected_admin': "❌ <b>Заявка #{request_id} отклонена</b>",
    'block_user_prompt': "🚫 <b>Заблокировать пользователя</b><br><br>Введите: <code>&lt;ID_пользователя&gt;</code><br><i>Пример</i>: <code>123456789</code><br>",
    'block_user_format': "❌ <b>Ошибка формата</b><br>Используйте: <code>&lt;ID_пользователя&gt;</code>",
    'user_blocked': "🚫 <b>Пользователь заблокирован</b>: <i>{user_id}</i>",
    'update_balance_prompt': "💰 <b>Изменить баланс</b><br><br>Введите: <code>&lt;ID_пользователя&gt; &lt;сумма&gt;</code><br><i>Пример</i>: <code>123456789 10.0</code><br>",
    'update_balance_format': "❌ <b>Ошибка формата</b><br>Используйте: <code>&lt;ID_пользователя&gt; &lt;сумма&gt;</code>",
    'balance_updated': "✅ <b>Баланс обновлён для</b>: <i>{user_id}</i>",
    'balance': "💸 <b>Ваш баланс, @{username}</b><br><br>💰 Сумма: <i>${balance}</i><br><br>Для вывода средств обратитесь в @PayoutBot 📤",
    'enter_phone': "➕ <b>Добавьте номер</b><br><br>Введите номер телефона:<br><i>Пример</i>: <code>79991234567</code> (с 7, без +)<br>",
    'invalid_phone': "❌ <b>Неверный номер</b><br>Должен быть 11 цифр, начинаться с 7 📞",
    'phone_in_queue': "🚫 <b>Номер уже в очереди</b><br>Попробуйте другой номер 📞",
    'max_numbers_reached': "🚫 <b>Лимит номеров: {max}</b><br>Дождитесь обработки текущих 📋",
    'error': "❌ <b>Упс, ошибка!</b><br>Попробуйте снова или свяжитесь с поддержкой 📩",
    'new_user': "👤 <b>Новый пользователь</b><br><br>👤 Пользователь: <i>@{username} ({user_id})</i><br>🕒 Дата: <i>{timestamp}</i>",
    'payout_welcome': "👋 <b>Привет, @{username}!</b><br>Добро пожаловать в <b>PayoutBot</b>! 💸<br><br>Используйте: <code>withdraw &lt;сумма&gt;</code>",
    'invalid_amount': "❌ <b>Неверная сумма</b><br>Сумма должна быть больше 0 💰",
    'not_registered': "🚫 <b>Вы не зарегистрированы</b><br>Зарегистрируйтесь в @StarRentBot",
    'insufficient_balance': "❌ <b>Недостаточно средств</b><br>Проверьте ваш баланс 💸",
    'withdraw_format': "❌ <b>Неверный формат</b><br>Используйте: <code>withdraw &lt;сумма&gt;</code><br><i>Пример</i>: <code>withdraw 10.0</code>",
    'new_payout': "💸 <b>Новая заявка на выплату #{payout_id}</b><br><br>👤 Пользователь: <i>@{username} ({user_id})</i><br>💰 Сумма: <i>${amount}</i>",
    'payout_submitted': "✅ <b>Заявка на выплату #{payout_id} создана</b><br>Ожидайте обработки 📤"
}