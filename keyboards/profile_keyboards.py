# keyboards/profile_keyboards.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_profile_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура личного кабинета"""
    buttons = [
        [InlineKeyboardButton(text="✏️ Изменить ник", callback_data="edit_nickname")],
        [InlineKeyboardButton(text="🌍 Изменить сервер", callback_data="edit_server")],
        [InlineKeyboardButton(text="📊 История покупок", callback_data="purchase_history")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_status_info_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура с информацией о статусах"""
    buttons = [
        [InlineKeyboardButton(text="📊 Подробнее о статусах", callback_data="status_details")],
        [InlineKeyboardButton(text="🔙 Назад в профиль", callback_data="profile")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)