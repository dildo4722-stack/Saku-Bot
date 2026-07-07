# database/users_db.py
from database.db import get_connection
from datetime import datetime

# database/users_db.py

def create_user(user_id: int, username: str = None, first_name: str = None, 
                last_name: str = None, referrer_id: int = None):
    """Создает нового пользователя"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Проверяем, существует ли пользователь
    cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
    existing_user = cursor.fetchone()
    
    if existing_user:
        # Обновляем данные существующего пользователя
        update_fields = []
        values = []
        
        if username:
            update_fields.append('username = ?')
            values.append(username)
        if first_name:
            update_fields.append('first_name = ?')
            values.append(first_name)
        if last_name:
            update_fields.append('last_name = ?')
            values.append(last_name)
        
        if update_fields:
            update_fields.append('updated_at = ?')
            values.append(datetime.now().isoformat())
            values.append(user_id)
            
            cursor.execute(f'''
                UPDATE users 
                SET {', '.join(update_fields)}
                WHERE user_id = ?
            ''', values)
    else:
        # Создаем нового пользователя
        cursor.execute('''
            INSERT INTO users (user_id, username, first_name, last_name, referrer_id, registration_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, username, first_name, last_name, referrer_id, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    
    return get_user(user_id)

def get_user(user_id: int):
    """Получает данные пользователя"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    
    conn.close()
    
    if user:
        return dict(user)
    return None

def update_user(user_id: int, **kwargs):
    """Обновляет данные пользователя"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Добавляем updated_at
    kwargs['updated_at'] = datetime.now().isoformat()
    
    # Формируем SET часть запроса
    set_clause = ', '.join([f"{key} = ?" for key in kwargs.keys()])
    values = list(kwargs.values()) + [user_id]
    
    cursor.execute(f'''
        UPDATE users 
        SET {set_clause}
        WHERE user_id = ?
    ''', values)
    
    conn.commit()
    conn.close()

def add_coins(user_id: int, amount: int, type: str = "purchase", 
              description: str = "", order_id: int = None):
    """Начисляет монеты пользователю"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Обновляем баланс
    cursor.execute('''
        UPDATE users 
        SET coins_balance = coins_balance + ?,
            updated_at = ?
        WHERE user_id = ?
    ''', (amount, datetime.now().isoformat(), user_id))
    
    # Записываем в историю
    cursor.execute('''
        INSERT INTO coins_history (user_id, amount, type, description, order_id)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, amount, type, description, order_id))
    
    conn.commit()
    conn.close()

def get_user_coins_balance(user_id: int) -> int:
    """Получает баланс монет пользователя"""
    user = get_user(user_id)
    return user['coins_balance'] if user else 0

def get_user_status(total_purchases: int) -> dict:
    """Определяет статус покупателя"""
    if total_purchases >= 400000:
        return {
            "name": "👑 Легенда Sakura",
            "emoji": "👑",
            "bonus_percent": 20
        }
    elif total_purchases >= 150000:
        return {
            "name": "💎 VIP Клиент",
            "emoji": "💎",
            "bonus_percent": 10
        }
    elif total_purchases >= 50000:
        return {
            "name": "🌸 Постоянный клиент",
            "emoji": "🌸",
            "bonus_percent": 0
        }
    else:
        return {
            "name": "🌱 Новичок",
            "emoji": "🌱",
            "bonus_percent": 0
        }