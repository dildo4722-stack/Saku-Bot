# database/admin_logs.py
from database.db import get_connection
from datetime import datetime

def add_log(action: str, admin_id: int, details: str = "", status: str = "success"):
    """Добавляет запись в лог"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO logs (action, admin_id, details, status, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (action, admin_id, details, status, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()

def get_logs(limit: int = 50, action: str = None):
    """Получает логи"""
    conn = get_connection()
    cursor = conn.cursor()
    
    if action:
        cursor.execute('''
            SELECT * FROM logs 
            WHERE action = ?
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (action, limit))
    else:
        cursor.execute('''
            SELECT * FROM logs 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
    
    logs = cursor.fetchall()
    conn.close()
    return [dict(log) for log in logs]