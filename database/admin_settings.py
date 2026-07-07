# database/admin_settings.py
from database.db import get_connection
import json

def get_setting(key: str, default=None):
    """Получает настройку"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        value = result['value']
        if value and (value.startswith('[') or value.startswith('{')):
            return json.loads(value)
        if value == 'True':
            return True
        if value == 'False':
            return False
        try:
            return int(value)
        except:
            return value
    return default

def set_setting(key: str, value):
    """Сохраняет настройку"""
    conn = get_connection()
    cursor = conn.cursor()
    
    if isinstance(value, (list, dict)):
        value = json.dumps(value, ensure_ascii=False)
    elif isinstance(value, bool):
        value = str(value)
    
    cursor.execute('''
        INSERT OR REPLACE INTO settings (key, value, updated_at)
        VALUES (?, ?, datetime('now'))
    ''', (key, str(value)))
    
    conn.commit()
    conn.close()

def init_settings():
    """Инициализация настроек по умолчанию"""
    from config import SHOP_SETTINGS
    for key, value in SHOP_SETTINGS.items():
        if get_setting(key) is None:
            set_setting(key, value)