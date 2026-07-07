# keyboards/main_menu.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_owner_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура владельца"""
    buttons = [
        [KeyboardButton(text="📦 Заказы"), KeyboardButton(text="👥 Пользователи")],
        [KeyboardButton(text="🛍 Товары"), KeyboardButton(text="🎟 Промокоды")],
        [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="📢 Рассылка")],
        [KeyboardButton(text="📰 Новости"), KeyboardButton(text="🌸 Новый вайп")],
        [KeyboardButton(text="⚙ Настройки"), KeyboardButton(text="📝 Логи")],
        [KeyboardButton(text="💾 Бэкап"), KeyboardButton(text="🏠 Обычное меню")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_manager_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура менеджера"""
    buttons = [
        [KeyboardButton(text="📦 Заказы"), KeyboardButton(text="👥 Пользователи")],
        [KeyboardButton(text="🏠 Обычное меню")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_moder_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура модератора"""
    buttons = [
        [KeyboardButton(text="📦 Заказы")],
        [KeyboardButton(text="🏠 Обычное меню")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_main_menu_keyboard(is_admin: bool = False, role: str = None) -> ReplyKeyboardMarkup:
    """Генерирует главное меню бота"""
    if is_admin:
        if role == "owner":
            return get_owner_keyboard()
        elif role == "manager":
            return get_manager_keyboard()
        elif role == "moder":
            return get_moder_keyboard()
    
    buttons = [
        [KeyboardButton(text="🛍 Магазин"), KeyboardButton(text="❤️ Кэшбэк")],
        [KeyboardButton(text="👥 Реферальная система"), KeyboardButton(text="🎟 Обмен монет")],
        [KeyboardButton(text="📦 Мои заказы"), KeyboardButton(text="📜 Правила")],
        [KeyboardButton(text="ℹ️ О магазине"), KeyboardButton(text="👤 Поддержка")],
        [KeyboardButton(text="👤 Личный кабинет")]
    ]
    
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        input_field_placeholder="Выберите интересующий раздел..."
    )