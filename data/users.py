# data/users.py
from datetime import datetime

# Временное хранилище пользователей (в будущем заменить на БД)
users_db = {}

def get_user_status(total_purchases: int) -> dict:
    """Определяет статус покупателя на основе общей суммы покупок"""
    if total_purchases >= 400000:
        return {
            "name": "👑 Легенда Sakura",
            "emoji": "👑",
            "benefits": [
                "Золотой значок",
                "+20% к кэшбэку",
                "Персональные скидки",
                "Отображение в ТОП покупателей",
                "Максимальный приоритет обработки заказов"
            ]
        }
    elif total_purchases >= 150000:
        return {
            "name": "💎 VIP Клиент",
            "emoji": "💎",
            "benefits": [
                "Значок 💎",
                "+10% к начисляемым Монетам",
                "Персональные акции",
                "Закрытые розыгрыши"
            ]
        }
    elif total_purchases >= 50000:
        return {
            "name": "🌸 Постоянный клиент",
            "emoji": "🌸",
            "benefits": [
                "Значок 🌸",
                "Ранний доступ к акциям",
                "Приоритетная проверка заказов"
            ]
        }
    else:
        return {
            "name": "🌱 Новичок",
            "emoji": "🌱",
            "benefits": [
                "Стандартный кэшбэк",
                "Участие в акциях"
            ]
        }

def get_user_data(user_id: int, username: str = None) -> dict:
    """Получает данные пользователя или создает нового"""
    if user_id not in users_db:
        users_db[user_id] = {
            "user_id": user_id,
            "username": username or "Не указан",
            "nickname": None,
            "server": None,
            "total_purchases": 0,
            "coins_balance": 0,
            "orders_count": 0,
            "referrals_count": 0,
            "registration_date": datetime.now().strftime("%d.%m.%Y"),
            "status": get_user_status(0)
        }
    elif username and users_db[user_id]["username"] == "Не указан":
        users_db[user_id]["username"] = username
    
    # Обновляем статус
    users_db[user_id]["status"] = get_user_status(users_db[user_id]["total_purchases"])
    
    return users_db[user_id]

def update_user_data(user_id: int, **kwargs):
    """Обновляет данные пользователя"""
    if user_id in users_db:
        users_db[user_id].update(kwargs)
        # Пересчитываем статус если изменились покупки
        if "total_purchases" in kwargs:
            users_db[user_id]["status"] = get_user_status(users_db[user_id]["total_purchases"])

# data/users.py (добавить в конец файла)

def add_coins_for_purchase(user_id: int, purchase_amount: int):
    """
    Начисляет монеты за покупку с учетом статуса пользователя
    """
    from handlers.cashback import calculate_cashback
    
    user_data = get_user_data(user_id)
    
    # Базовый кэшбэк
    base_coins = calculate_cashback(purchase_amount)
    
    # Бонус в зависимости от статуса
    status = user_data["status"]
    bonus_multiplier = 1.0
    
    if status["name"] == "👑 Легенда Sakura":
        bonus_multiplier = 1.2  # +20%
    elif status["name"] == "💎 VIP Клиент":
        bonus_multiplier = 1.1  # +10%
    
    total_coins = int(base_coins * bonus_multiplier)
    
    # Начисляем монеты
    user_data["coins_balance"] = user_data.get("coins_balance", 0) + total_coins
    
    # Обновляем общую сумму покупок
    user_data["total_purchases"] = user_data.get("total_purchases", 0) + purchase_amount
    user_data["orders_count"] = user_data.get("orders_count", 0) + 1
    
    # Обновляем статус
    user_data["status"] = get_user_status(user_data["total_purchases"])
    
    return total_coins