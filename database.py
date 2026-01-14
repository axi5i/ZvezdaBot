import sqlite3
import os
from datetime import datetime

DB_FILE = "bot_data.db"

def init_db():
    """Инициализация базы данных"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            full_name TEXT,
            balance REAL DEFAULT 3,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Таблица рефералов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS referrals (
            invited_id INTEGER PRIMARY KEY,
            inviter_id INTEGER,
            awarded INTEGER DEFAULT 0
        )
    ''')
    
    # Таблица заявок на обмен подарков
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gift_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            gift_name TEXT,
            cost INTEGER,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Таблица заявок на ввод звёзд
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS star_input_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount REAL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Таблица спонсоров
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sponsors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_name TEXT UNIQUE,
            added_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1
        )
    ''')
    
    # Таблица заданий
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sponsor_id INTEGER,
            sponsor_name TEXT,
            last_reset TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_users TEXT DEFAULT '',
            FOREIGN KEY(sponsor_id) REFERENCES sponsors(id)
        )
    ''')
    
    # Таблица выполненных заданий пользователями
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            task_id INTEGER,
            completed_today INTEGER DEFAULT 0,
            last_completed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(task_id) REFERENCES tasks(id)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_user_balance(user_id: int) -> float:
    """Получить баланс пользователя"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 3.0

def add_user(user_id: int, full_name: str, balance: float = 3):
    """Добавить нового пользователя"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users (user_id, full_name, balance) VALUES (?, ?, ?)',
                      (user_id, full_name, balance))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()

def update_balance(user_id: int, amount: float):
    """Обновить баланс пользователя"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', (amount, user_id))
    conn.commit()
    conn.close()

def add_referral(invited_id: int, inviter_id: int):
    """Добавить реферала"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO referrals (invited_id, inviter_id) VALUES (?, ?)',
                      (invited_id, inviter_id))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()

def mark_referral_awarded(invited_id: int):
    """Отметить реферала как вознаграждённого"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('UPDATE referrals SET awarded = 1 WHERE invited_id = ?', (invited_id,))
    conn.commit()
    conn.close()

def is_referral_awarded(invited_id: int) -> bool:
    """Проверить, получена ли награда за реферала"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT awarded FROM referrals WHERE invited_id = ?', (invited_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else False

def get_referral_inviter(invited_id: int) -> int:
    """Получить ID инвайтера для реферала"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT inviter_id FROM referrals WHERE invited_id = ?', (invited_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def user_exists(user_id: int) -> bool:
    """Проверить, существует ли пользователь"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def get_all_users():
    """Получить всех пользователей"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM users')
    result = cursor.fetchall()
    conn.close()
    return [row[0] for row in result]

def add_gift_request(user_id: int, gift_name: str, cost: int):
    """Добавить заявку на подарок"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO gift_requests (user_id, gift_name, cost) VALUES (?, ?, ?)',
                  (user_id, gift_name, cost))
    conn.commit()
    conn.close()

def add_star_input_request(user_id: int, amount: float):
    """Добавить заявку на ввод звёзл"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO star_input_requests (user_id, amount) VALUES (?, ?)',
                  (user_id, amount))
    conn.commit()
    conn.close()


# ============ СПОНСОРЫ И ЗАДАНИЯ ============

def add_sponsor(channel_name: str, added_by: int) -> int:
    """Добавить спонсора"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO sponsors (channel_name, added_by) VALUES (?, ?)',
                      (channel_name, added_by))
        conn.commit()
        sponsor_id = cursor.lastrowid
        conn.close()
        return sponsor_id
    except sqlite3.IntegrityError:
        conn.close()
        return None

def get_active_sponsors():
    """Получить всех активных спонсоров"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, channel_name FROM sponsors WHERE is_active = 1')
    result = cursor.fetchall()
    conn.close()
    return result

def remove_sponsor(channel_name: str):
    """Удалить спонсора"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('UPDATE sponsors SET is_active = 0 WHERE channel_name = ?', (channel_name,))
    conn.commit()
    conn.close()

def get_or_create_task(sponsor_id: int, sponsor_name: str):
    """Получить или создать задание на день"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Проверяем, есть ли задание на сегодня
    cursor.execute('''
        SELECT id FROM tasks 
        WHERE sponsor_id = ? AND date(last_reset) = date('now')
    ''', (sponsor_id,))
    
    result = cursor.fetchone()
    if result:
        conn.close()
        return result[0]
    
    # Создаём новое задание на день
    cursor.execute('''
        INSERT INTO tasks (sponsor_id, sponsor_name) VALUES (?, ?)
    ''', (sponsor_id, sponsor_name))
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()
    return task_id

def mark_task_completed(user_id: int, task_id: int):
    """Отметить задание как выполненное для пользователя"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO user_tasks (user_id, task_id, completed_today)
        VALUES (?, ?, 1)
    ''', (user_id, task_id))
    
    conn.commit()
    conn.close()

def is_task_completed_today(user_id: int, task_id: int) -> bool:
    """Проверить, выполнил ли пользователь задание сегодня"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT completed_today FROM user_tasks 
        WHERE user_id = ? AND task_id = ? AND date(last_completed) = date('now')
    ''', (user_id, task_id))
    
    result = cursor.fetchone()
    conn.close()
    return bool(result and result[0])


# ============ РЕЙТИНГ ============

def get_top_users(limit: int = 10):
    """Получить топ пользователей по балансу"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT user_id, full_name, balance FROM users 
        ORDER BY balance DESC LIMIT ?
    ''', (limit,))
    result = cursor.fetchall()
    conn.close()
    return result

def get_user_rank(user_id: int) -> int:
    """Получить ранг пользователя в рейтинге"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT balance FROM users WHERE user_id = ?
    ''', (user_id,))
    user_balance = cursor.fetchone()
    
    if not user_balance:
        conn.close()
        return None
    
    cursor.execute('''
        SELECT COUNT(*) FROM users WHERE balance > ?
    ''', (user_balance[0],))
    rank = cursor.fetchone()[0] + 1
    conn.close()
    return rank

def get_user_info(user_id: int):
    """Получить информацию пользователя"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, full_name, balance FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result
