# handlers/exchange.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from database.users_db import get_user

router = Router()

EXCHANGE_TEXT = (
    "♻️ *Обмен Монет*\n\n"
    "Здесь вы можете обменять накопленные Монеты 🍀 на товары.\n\n"
    
    "⸻\n\n"
    
    "*🧸 Питомцы*\n"
    "🐝 Пчела — 50🪙\n"
    "🦊 Лиса — 135🪙\n"
    "🐼 Панда — 400🪙\n"
    "🦈 Аксолотль — 1000🪙\n\n"
    
    "*🛡 Привилегии*\n"
    "🛡 Флай — 50🪙\n"
    "🛡 VIP — 100🪙\n"
    "🛡 Креатив — 350🪙\n"
    "🛡 Админ — 660🪙\n\n"
    
    "*🎀 Telegram\\-подарки*\n"
    "🧸 Мишка — 20🪙\n"
    "💝 Сердце — 20🪙\n"
    "🌹 Роза — 35🪙\n"
    "🎁 Подарок — 35🪙\n"
    "🚀 Ракета — 70🪙\n"
    "🎂 Торт — 70🪙\n"
    "💐 Букет — 70🪙\n"
    "💍 Кольцо — 135🪙\n"
    "🏆 Кубок — 135🪙\n"
    "💎 Бриллиант — 135🪙\n\n"
    
    "🎉 Подарки стоимостью 100⭐ можно приобрести за 135🪙 вместо 140🪙\n\n"
    
    "⸻\n\n"
    
    "📩 *Для обмена монет свяжитесь с тех\\-поддержкой:*\n"
    "@Help\\_Sakura\\_Stor\\_bot"
)

def get_exchange_keyboard(user_coins: int = 0) -> InlineKeyboardMarkup:
    """Клавиатура для обмена монет"""
    buttons = [
        [InlineKeyboardButton(text="💬 Тех. поддержка", url="https://t.me/Help_Sakura_Stor_bot")],
        [InlineKeyboardButton(text="👤 Личный кабинет", callback_data="profile")],
        [InlineKeyboardButton(text="❤️ Кэшбэк", callback_data="cashback")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@router.message(F.text == "🎟 Обмен монет")
async def show_exchange(message: Message):
    """Показывает раздел обмена монет"""
    user_data = get_user(message.from_user.id)
    coins_balance = user_data['coins_balance'] if user_data else 0
    
    # Добавляем информацию о балансе
    balance_text = f"🍀 *Ваш баланс:* {coins_balance} 🪙\n\n"
    full_text = balance_text + EXCHANGE_TEXT
    
    await message.answer(
        full_text,
        reply_markup=get_exchange_keyboard(coins_balance),
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

@router.callback_query(F.data == "exchange")
async def show_exchange_callback(callback: CallbackQuery):
    """Показывает обмен монет через callback"""
    user_data = get_user(callback.from_user.id)
    coins_balance = user_data['coins_balance'] if user_data else 0
    
    balance_text = f"🍀 *Ваш баланс:* {coins_balance} 🪙\n\n"
    full_text = balance_text + EXCHANGE_TEXT
    
    await callback.message.edit_text(
        full_text,
        reply_markup=get_exchange_keyboard(coins_balance),
        parse_mode="Markdown",
        disable_web_page_preview=True
    )