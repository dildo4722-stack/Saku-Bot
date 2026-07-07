# database/admin_db.py
from database.db import get_connection
from config import ADMIN_IDS, MANAGER_IDS, MODER_IDS
from datetime import datetime

def get_admin_role(user_id: int) -> str:
    """Возвращает роль администратора"""
    if user_id in ADMIN_IDS:
        return "owner"
    elif user_id in MANAGER_IDS:
        return "manager"
    elif user_id in MODER_IDS:
        return "moder"
    return None

def is_admin(user_id: int) -> bool:
    """Проверяет, является ли пользователь администратором (любая роль)"""
    return user_id in ADMIN_IDS or user_id in MANAGER_IDS or user_id in MODER_IDS

def add_manager(user_id: int):
    """Добавляет менеджера"""
    if user_id not in MANAGER_IDS:
        MANAGER_IDS.append(user_id)
        return True
    return False

def add_moder(user_id: int):
    """Добавляет модератора"""
    if user_id not in MODER_IDS:
        MODER_IDS.append(user_id)
        return True
    return False

def get_all_orders(status: str = None):
    """Получает все заказы"""
    conn = get_connection()
    cursor = conn.cursor()
    
    if status:
        cursor.execute('''
            SELECT o.*, u.username, u.first_name 
            FROM orders o
            JOIN users u ON o.user_id = u.user_id
            WHERE o.status = ?
            ORDER BY o.created_at DESC
        ''', (status,))
    else:
        cursor.execute('''
            SELECT o.*, u.username, u.first_name 
            FROM orders o
            JOIN users u ON o.user_id = u.user_id
            ORDER BY o.created_at DESC
        ''')
    
    orders = cursor.fetchall()
    conn.close()
    return [dict(order) for order in orders]

def update_order_status(order_id: int, status: str, admin_id: int):
    """Обновляет статус заказа"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE orders SET status = ?, updated_at = datetime("now") WHERE order_id = ?', (status, order_id))
    conn.commit()
    conn.close()

def get_order_by_id(order_id: int):
    """Получает заказ по ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT o.*, u.username, u.first_name FROM orders o JOIN users u ON o.user_id = u.user_id WHERE o.order_id = ?', (order_id,))
    order = cursor.fetchone()
    conn.close()
    return dict(order) if order else None

def delete_order(order_id: int):
    """Удаляет заказ"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM order_items WHERE order_id = ?', (order_id,))
    cursor.execute('DELETE FROM orders WHERE order_id = ?', (order_id,))
    conn.commit()
    conn.close()

def get_orders_count_by_status():
    """Количество заказов по статусам"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT status, COUNT(*) as count FROM orders GROUP BY status')
    result = cursor.fetchall()
    conn.close()
    return {row['status']: row['count'] for row in result}

def get_all_users():
    """Получает всех пользователей"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users ORDER BY registration_date DESC')
    users = cursor.fetchall()
    conn.close()
    return [dict(user) for user in users]

def get_user_by_id(user_id: int):
    """Получает пользователя по ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def update_user_admin(user_id: int, **kwargs):
    """Обновляет пользователя (админ)"""
    conn = get_connection()
    cursor = conn.cursor()
    set_clause = ', '.join([f"{key} = ?" for key in kwargs.keys()])
    values = list(kwargs.values()) + [user_id]
    cursor.execute(f'UPDATE users SET {set_clause} WHERE user_id = ?', values)
    conn.commit()
    conn.close()

def delete_user_admin(user_id: int):
    """Удаляет пользователя"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM order_items WHERE order_id IN (SELECT order_id FROM orders WHERE user_id = ?)', (user_id,))
    cursor.execute('DELETE FROM orders WHERE user_id = ?', (user_id,))
    cursor.execute('DELETE FROM referrals WHERE referrer_id = ? OR referred_id = ?', (user_id, user_id))
    cursor.execute('DELETE FROM coins_history WHERE user_id = ?', (user_id,))
    cursor.execute('DELETE FROM promocode_uses WHERE user_id = ?', (user_id,))
    cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

def get_statistics():
    """Общая статистика"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) as count FROM users')
    total_users = cursor.fetchone()['count']
    cursor.execute('SELECT COUNT(*) as count FROM orders')
    total_orders = cursor.fetchone()['count']
    cursor.execute('SELECT COALESCE(SUM(total_amount), 0) as total FROM orders WHERE status = "completed"')
    total_sales = cursor.fetchone()['total']
    cursor.execute('SELECT COUNT(*) as count FROM orders WHERE date(created_at) = date("now")')
    today_orders = cursor.fetchone()['count']
    conn.close()
    return {'total_users': total_users, 'total_orders': total_orders, 'total_sales': total_sales, 'today_orders': today_orders}

def reset_all_coins():
    """Обнуляет все монеты"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET coins_balance = 0')
    cursor.execute('DELETE FROM coins_history')
    conn.commit()
    conn.close()

def reset_referrals():
    """Сбрасывает реферальные бонусы"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE referrals SET bonus_earned = 0')
    conn.commit()
    conn.close()

def add_referral_bonus(referrer_id: int, referred_id: int, order_id: int, bonus_amount: int):
    """Начисляет бонус рефереру"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Обновляем бонус в таблице рефералов
        cursor.execute('''
            UPDATE referrals 
            SET bonus_earned = bonus_earned + ?
            WHERE referrer_id = ? AND referred_id = ?
        ''', (bonus_amount, referrer_id, referred_id))
        
        # Начисляем монеты рефереру (без вызова add_coins)
        cursor.execute('''
            UPDATE users 
            SET coins_balance = coins_balance + ?,
                updated_at = ?
            WHERE user_id = ?
        ''', (bonus_amount, datetime.now().isoformat(), referrer_id))
        
        # Записываем в историю
        cursor.execute('''
            INSERT INTO coins_history (user_id, amount, type, description, order_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (referrer_id, bonus_amount, "referral", 
              f"Бонус за покупку реферала (заказ #{order_id})", order_id))
        
        conn.commit()
    except:
        conn.rollback()
        raise
    finally:
        conn.close()