# keyboards/admin_keyboards.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton



def get_admin_main_keyboard() -> InlineKeyboardMarkup:
    """Инлайн главное меню админа"""
    buttons = [
        [InlineKeyboardButton(text="📦 Заказы", callback_data="admin_orders")],
        [InlineKeyboardButton(text="👥 Пользователи", callback_data="admin_users")],
        [InlineKeyboardButton(text="🛍 Товары", callback_data="admin_products")],
        [InlineKeyboardButton(text="🎟 Промокоды", callback_data="admin_promocodes")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📢 Рассылка", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="📰 Новости", callback_data="admin_news")],
        [InlineKeyboardButton(text="🌸 Новый вайп", callback_data="admin_wipe")],
        [InlineKeyboardButton(text="⚙ Настройки", callback_data="admin_settings")],
        [InlineKeyboardButton(text="📝 Логи", callback_data="admin_logs")],
        [InlineKeyboardButton(text="💾 Бэкап", callback_data="admin_backup")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)