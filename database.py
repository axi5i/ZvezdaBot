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
