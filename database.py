import sqlite3
from datetime import datetime
import logging
from config import DATABASE_PATH, REF_CODE, ERROR_DATABASE

logger = logging.getLogger(__name__)

def get_db_connection():
    """Получение соединения с базой данных"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        logger.error(ERROR_DATABASE.format(e))
        raise

def init_db():
    """Инициализация базы данных с индексами"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.executescript('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT,
                secret_code TEXT,
                balance REAL DEFAULT 0.0,
                is_blocked INTEGER DEFAULT 0
            );
            CREATE INDEX IF NOT EXISTS idx_users_user_id ON users(user_id);

            CREATE TABLE IF NOT EXISTS secret_codes (
                code TEXT PRIMARY KEY,
                is_one_time INTEGER,
                max_uses INTEGER,
                current_uses INTEGER DEFAULT 0,
                creator_id TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_codes_code ON secret_codes(code);

            CREATE TABLE IF NOT EXISTS queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                phone_number TEXT UNIQUE,
                position INTEGER,
                notified INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_queue_user_id ON queue(user_id);

            CREATE TABLE IF NOT EXISTS archive (
                phone_number TEXT,
                status TEXT,
                amount REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_archive_phone ON archive(phone_number);

            CREATE TABLE IF NOT EXISTS payouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                amount REAL,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_payouts_user_id ON payouts(user_id);

            CREATE TABLE IF NOT EXISTS support_tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                question TEXT,
                response TEXT,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_tickets_user_id ON support_tickets(user_id);

            CREATE TABLE IF NOT EXISTS rent_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                phone_number TEXT,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_requests_user_id ON rent_requests(user_id);
        ''')
        cursor.execute('SELECT COUNT(*) FROM secret_codes WHERE code = ?', (REF_CODE,))
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                'INSERT INTO secret_codes (code, is_one_time, max_uses, current_uses, creator_id) VALUES (?, ?, ?, ?, ?)',
                (REF_CODE, 0, 1000, 0, 'system')
            )
        conn.commit()
    except Exception as e:
        logger.error(ERROR_DATABASE.format(e))
        raise
    finally:
        conn.close()

def add_user(user_id: str, username: str, secret_code: str) -> tuple:
    """Добавление пользователя"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM secret_codes WHERE code = ?', (secret_code,))
        code = cursor.fetchone()
        if not code:
            return False, "Неверный реферальный код."
        if code['is_one_time'] and code['current_uses'] >= 1:
            return False, "Этот код уже использован."
        if code['current_uses'] >= code['max_uses']:
            return False, "Код достиг максимума использований."
        cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
        if cursor.fetchone():
            return False, "Вы уже зарегистрированы."
        cursor.execute(
            'INSERT INTO users (user_id, username, secret_code) VALUES (?, ?, ?)',
            (user_id, username, secret_code)
        )
        cursor.execute(
            'UPDATE secret_codes SET current_uses = current_uses + 1 WHERE code = ?',
            (secret_code,)
        )
        conn.commit()
        return True, "Регистрация успешна! Выберите действие:"
    except Exception as e:
        logger.error(f"Ошибка при добавлении пользователя: {e}")
        return False, "Ошибка при регистрации."
    finally:
        conn.close()

def add_to_queue(user_id: str, phone_number: str) -> tuple:
    """Добавление номера в очередь"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT phone_number FROM archive WHERE phone_number = ?', (phone_number,))
        if cursor.fetchone():
            return False, "Номер уже использован в архиве."
        cursor.execute('SELECT MAX(position) FROM queue')
        max_position = cursor.fetchone()[0] or 0
        new_position = max_position + 1
        cursor.execute(
            'INSERT INTO queue (user_id, phone_number, position) VALUES (?, ?, ?)',
            (user_id, phone_number, new_position)
        )
        conn.commit()
        return True, "Номер добавлен. Заявка на аренду отправлена."
    except sqlite3.IntegrityError:
        return False, "Номер уже в очереди."
    except Exception as e:
        logger.error(f"Ошибка при добавлении в очередь: {e}")
        return False, "Ошибка при добавлении номера."
    finally:
        conn.close()

def create_rent_request(user_id: str, phone_number: str) -> int:
    """Создание заявки на аренду"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO rent_requests (user_id, phone_number, status) VALUES (?, ?, ?)',
            (user_id, phone_number, 'pending')
        )
        request_id = cursor.lastrowid
        conn.commit()
        return request_id
    except Exception as e:
        logger.error(f"Ошибка при создании заявки: {e}")
        raise
    finally:
        conn.close()

def create_support_ticket(user_id: str, question: str) -> int:
    """Создание тикета в поддержку"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO support_tickets (user_id, question, status) VALUES (?, ?, ?)',
            (user_id, question, 'open')
        )
        ticket_id = cursor.lastrowid
        conn.commit()
        return ticket_id
    except Exception as e:
        logger.error(f"Ошибка при создании тикета: {e}")
        raise
    finally:
        conn.close()

def get_rent_requests():
    """Получение всех заявок"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM rent_requests ORDER BY created_at DESC')
        return cursor.fetchall()
    except Exception as e:
        logger.error(f"Ошибка при получении заявок: {e}")
        return []
    finally:
        conn.close()

def update_rent_request_status(request_id: int, status: str):
    """Обновление статуса заявки"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE rent_requests SET status = ? WHERE id = ?',
            (status, request_id)
        )
        conn.commit()
    except Exception as e:
        logger.error(f"Ошибка при обновлении заявки: {e}")
        raise
    finally:
        conn.close()

def get_queue():
    """Получение очереди"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM queue ORDER BY position')
        return cursor.fetchall()
    except Exception as e:
        logger.error(f"Ошибка при получении очереди: {e}")
        return []
    finally:
        conn.close()

def get_user(user_id: str):
    """Получение пользователя"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        return cursor.fetchone()
    except Exception as e:
        logger.error(f"Ошибка при получении пользователя: {e}")
        return None
    finally:
        conn.close()

def get_user_archive(user_id: str):
    """Получение архива пользователя"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT phone_number, status, amount FROM archive WHERE phone_number IN (SELECT phone_number FROM queue WHERE user_id = ?)',
            (user_id,)
        )
        return cursor.fetchall()
    except Exception as e:
        logger.error(f"Ошибка при получении архива: {e}")
        return []
    finally:
        conn.close()

def get_stats():
    """Получение статистики"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM users')
        total_users = cursor.fetchone()[0]
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute('SELECT COUNT(*) FROM queue WHERE DATE(created_at) = ?', (today,))
        today_numbers = cursor.fetchone()[0]
        return total_users, today_numbers
    except Exception as e:
        logger.error(f"Ошибка при получении статистики: {e}")
        return 0, 0
    finally:
        conn.close()

def get_secret_codes():
    """Получение реферальных кодов"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM secret_codes')
        return cursor.fetchall()
    except Exception as e:
        logger.error(f"Ошибка при получении кодов: {e}")
        return []
    finally:
        conn.close()

def create_secret_code(code: str, max_uses: int):
    """Создание реферального кода"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO secret_codes (code, is_one_time, max_uses, current_uses, creator_id) VALUES (?, ?, ?, ?, ?)',
            (code, 0, max_uses, 0, 'admin')
        )
        conn.commit()
    except Exception as e:
        logger.error(f"Ошибка при создании кода: {e}")
        raise
    finally:
        conn.close()

def move_to_archive(queue_id: int, status: str, amount: float):
    """Перемещение номера в архив"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT phone_number, position FROM queue WHERE id = ?', (queue_id,))
        phone = cursor.fetchone()
        if phone:
            cursor.execute(
                'INSERT INTO archive (phone_number, status, amount) VALUES (?, ?, ?)',
                (phone['phone_number'], status, amount)
            )
            cursor.execute('DELETE FROM queue WHERE id = ?', (queue_id,))
            cursor.execute(
                'UPDATE queue SET position = position - 1 WHERE position > ?',
                (phone['position'],)
            )
            cursor.execute(
                'UPDATE queue SET notified = 0 WHERE position = 3 AND notified = 1'
            )
        conn.commit()
    except Exception as e:
        logger.error(f"Ошибка при перемещении в архив: {e}")
        raise
    finally:
        conn.close()

def block_user(user_id: str):
    """Блокировка пользователя"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE users SET is_blocked = 1 WHERE user_id = ?',
            (user_id,)
        )
        conn.commit()
    except Exception as e:
        logger.error(f"Ошибка при блокировке пользователя: {e}")
        raise
    finally:
        conn.close()

def get_payouts():
    """Получение списка выплат"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM payouts ORDER BY created_at DESC')
        return cursor.fetchall()
    except Exception as e:
        logger.error(f"Ошибка при получении выплат: {e}")
        return []
    finally:
        conn.close()

def update_payout(payout_id: int, status: str):
    """Обновление статуса выплаты"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE payouts SET status = ? WHERE id = ?',
            (status, payout_id)
        )
        conn.commit()
    except Exception as e:
        logger.error(f"Ошибка при обновлении выплаты: {e}")
        raise
    finally:
        conn.close()

def get_support_tickets():
    """Получение списка тикетов"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM support_tickets ORDER BY created_at DESC')
        return cursor.fetchall()
    except Exception as e:
        logger.error(f"Ошибка при получении тикетов: {e}")
        return []
    finally:
        conn.close()

def respond_to_ticket(ticket_id: int, response: str):
    """Ответ на тикет"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE support_tickets SET response = ?, status = ? WHERE id = ?',
            (response, 'answered', ticket_id)
        )
        conn.commit()
    except Exception as e:
        logger.error(f"Ошибка при ответе на тикет: {e}")
        raise
    finally:
        conn.close()

def update_balance(user_id: str, amount: float):
    """Обновление баланса пользователя"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE users SET balance = balance + ? WHERE user_id = ?',
            (amount, user_id)
        )
        conn.commit()
    except Exception as e:
        logger.error(f"Ошибка при обновлении баланса: {e}")
        raise
    finally:
        conn.close()