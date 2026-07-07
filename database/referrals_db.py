# database/referrals_db.py
from database.db import get_connection
from datetime import datetime

def add_referral(referrer_id: int, referred_id: int):
    """Добавляет реферала"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Проверяем, не существует ли уже такая связь
    cursor.execute('''
        SELECT id FROM referrals 
        WHERE referrer_id = ? AND referred_id = ?
    ''', (referrer_id, referred_id))
    
    if cursor.fetchone():
        conn.close()
        return False
    
    # Добавляем реферала
    cursor.execute('''
        INSERT INTO referrals (referrer_id, referred_id, created_at)
        VALUES (?, ?, ?)
    ''', (referrer_id, referred_id, datetime.now().isoformat()))
    
    # Обновляем счетчик рефералов у пригласившего
    cursor.execute('''
        UPDATE users 
        SET referrals_count = referrals_count + 1,
            updated_at = ?
        WHERE user_id = ?
    ''', (datetime.now().isoformat(), referrer_id))
    
    conn.commit()
    conn.close()
    return True

def get_user_referrals(user_id: int):
    """Получает список рефералов пользователя"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT r.*, u.username, u.first_name, u.total_purchases
        FROM referrals r
        JOIN users u ON r.referred_id = u.user_id
        WHERE r.referrer_id = ?
        ORDER BY r.created_at DESC
    ''', (user_id,))
    
    referrals = cursor.fetchall()
    conn.close()
    
    return [dict(ref) for ref in referrals]

def get_referrer(user_id: int):
    """Получает информацию о том, кто пригласил пользователя"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT referrer_id FROM users
        WHERE user_id = ?
    ''', (user_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    return result['referrer_id'] if result else None

def calculate_referral_bonus(purchase_amount: int, referral_percent: float = 0.02) -> int:
    """
    Рассчитывает бонус реферера от покупки реферала
    Стандартно 2% от суммы покупки
    """
    return int(purchase_amount * referral_percent)

def add_referral_bonus(referrer_id: int, referred_id: int, 
                       order_id: int, bonus_amount: int):
    """Начисляет бонус рефереру за покупку реферала"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Обновляем бонус в таблице рефералов
    cursor.execute('''
        UPDATE referrals 
        SET bonus_earned = bonus_earned + ?
        WHERE referrer_id = ? AND referred_id = ?
    ''', (bonus_amount, referrer_id, referred_id))
    
        
    cursor.execute('''
        UPDATE users 
        SET coins_balance = coins_balance + ?,
            updated_at = ?
        WHERE user_id = ?
    ''', (bonus_amount, datetime.now().isoformat(), referrer_id))
    
    cursor.execute('''
        INSERT INTO coins_history (user_id, amount, type, description, order_id)
        VALUES (?, ?, ?, ?, ?)
    ''', (referrer_id, bonus_amount, "referral", 
          f"Бонус за покупку реферала (заказ #{order_id})", order_id))
    
    conn.commit()
    conn.close()

def get_total_referral_bonus(user_id: int) -> int:
    """Получает общую сумму бонусов за рефералов"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT COALESCE(SUM(bonus_earned), 0) as total_bonus
        FROM referrals
        WHERE referrer_id = ?
    ''', (user_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    return result['total_bonus'] if result else 0