# database/promocodes_db.py
from database.db import get_connection
from datetime import datetime

def create_promocode(code: str, discount_percent: int, max_uses: int = None, 
                     min_amount: int = 0, valid_until: str = None):
    """Создает новый промокод"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO promocodes (code, discount_percent, max_uses, uses_count, 
                               min_amount, valid_until, is_active)
        VALUES (?, ?, ?, 0, ?, ?, 1)
    ''', (code.upper(), discount_percent, max_uses, min_amount, valid_until))
    
    conn.commit()
    conn.close()

def check_promocode(code: str, user_id: int, order_amount: int) -> dict:
    """Проверяет валидность промокода"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Ищем промокод
    cursor.execute('''
        SELECT * FROM promocodes 
        WHERE code = ? AND is_active = 1
    ''', (code.upper(),))
    
    promocode = cursor.fetchone()
    
    if not promocode:
        conn.close()
        return {"valid": False, "message": "❌ Промокод не найден"}
    
    promocode = dict(promocode)
    
    # Проверяем срок действия
    if promocode['valid_until']:
        valid_until = datetime.fromisoformat(promocode['valid_until'])
        if datetime.now() > valid_until:
            conn.close()
            return {"valid": False, "message": "❌ Срок действия промокода истек"}
    
    # Проверяем количество использований
    if promocode['max_uses'] and promocode['uses_count'] >= promocode['max_uses']:
        conn.close()
        return {"valid": False, "message": "❌ Промокод больше не действителен"}
    
    # Проверяем минимальную сумму
    if order_amount < promocode['min_amount']:
        conn.close()
        return {
            "valid": False, 
            "message": f"❌ Минимальная сумма заказа: {promocode['min_amount']}💵"
        }
    
    # Проверяем, не использовал ли пользователь этот промокод
    cursor.execute('''
        SELECT id FROM promocode_uses 
        WHERE promocode_id = ? AND user_id = ?
    ''', (promocode['id'], user_id))
    
    if cursor.fetchone():
        conn.close()
        return {"valid": False, "message": "❌ Вы уже использовали этот промокод"}
    
    conn.close()
    
    return {
        "valid": True,
        "message": f"✅ Промокод применен! Скидка {promocode['discount_percent']}%",
        "discount_percent": promocode['discount_percent'],
        "promocode_id": promocode['id']
    }

def use_promocode(promocode_id: int, user_id: int, order_id: int):
    """Отмечает использование промокода"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Записываем использование
    cursor.execute('''
        INSERT INTO promocode_uses (promocode_id, user_id, order_id)
        VALUES (?, ?, ?)
    ''', (promocode_id, user_id, order_id))
    
    # Увеличиваем счетчик использований
    cursor.execute('''
        UPDATE promocodes 
        SET uses_count = uses_count + 1 
        WHERE id = ?
    ''', (promocode_id,))
    
    conn.commit()
    conn.close()