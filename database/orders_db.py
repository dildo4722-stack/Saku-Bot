# database/orders_db.py
from database.db import get_connection
from datetime import datetime

def create_order(user_id: int, total_amount: int, discount: int = 0,
                 coins_earned: int = 0, payment_method: str = None,
                 server: str = None, nickname: str = None, screenshot_id: str = None) -> int:
    """Создает новый заказ"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO orders (user_id, total_amount, discount, coins_earned, 
                          payment_method, server, nickname, screenshot_id, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending')
    ''', (user_id, total_amount, discount, coins_earned, payment_method, server, nickname, screenshot_id))
    
    order_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return order_id

def add_order_item(order_id: int, product_id: int, product_name: str, 
                   price: int, quantity: int):
    """Добавляет товар в заказ"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO order_items (order_id, product_id, product_name, price, quantity)
        VALUES (?, ?, ?, ?, ?)
    ''', (order_id, product_id, product_name, price, quantity))
    
    conn.commit()
    conn.close()

def update_order_status(order_id: int, status: str, screenshot_id: str = None):
    """Обновляет статус заказа"""
    conn = get_connection()
    cursor = conn.cursor()
    
    if screenshot_id:
        cursor.execute('''
            UPDATE orders 
            SET status = ?, screenshot_id = ?, updated_at = ?
            WHERE order_id = ?
        ''', (status, screenshot_id, datetime.now().isoformat(), order_id))
    else:
        cursor.execute('''
            UPDATE orders 
            SET status = ?, updated_at = ?
            WHERE order_id = ?
        ''', (status, datetime.now().isoformat(), order_id))
    
    conn.commit()
    conn.close()

def get_user_orders(user_id: int):
    """Получает заказы пользователя"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM orders 
        WHERE user_id = ? 
        ORDER BY created_at DESC
    ''', (user_id,))
    
    orders = cursor.fetchall()
    conn.close()
    
    return [dict(order) for order in orders]

def get_order_items(order_id: int):
    """Получает товары в заказе"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM order_items 
        WHERE order_id = ?
    ''', (order_id,))
    
    items = cursor.fetchall()
    conn.close()
    
    return [dict(item) for item in items]