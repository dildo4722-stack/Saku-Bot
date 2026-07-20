# handlers/cashback.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from database.users_db import get_user, create_user, get_user_status
from database.supabase_client import get_combined_coins

router = Router()

def calculate_cashback(amount: int) -> int:
    """
    Рассчитывает кэшбэк в монетах от суммы покупки.
    5000 = 5🍀
    10000 = 10🍀
    30000 = 30🍀
    60000 = 60🍀
    100000 = 100🍀
    Далее — 1🍀 за каждую 1000💵
    """
    cashback_rates = {
        5000: 5,
        10000: 10,
        30000: 30,
        60000: 60,
        100000: 100
    }
    
    if amount in cashback_rates:
        return cashback_rates[amount]
    
    if amount > 100000:
        coins = 100
        extra_amount = amount - 100000
        coins += extra_amount // 1000
        return coins
    
    if amount > 60000:
        return 60
    elif amount > 30000:
        return 30
    elif amount > 10000:
        return 10
    elif amount > 5000:
        return 5
    else:
        return amount // 1000

def get_cashback_info_message(status: dict, total_coins: int) -> str:
    """Формирует сообщение с информацией о кэшбэке"""
    if status["name"] == "👑 Легенда Sakura":
        bonus_text = "+20% к кэшбэку"
    elif status["name"] == "💎 VIP Клиент":
        bonus_text = "+10% к Монетам"
    else:
        bonus_text = "Стандартный кэшбэк"
    
    message = (
        f"💰 *Кэшбэк*\n\n"
        f"🍀 *Ваш баланс Монет:* {total_coins} 🍀\n"
        f"👑 *Статус:* {status['emoji']} {status['name']}\n"
        f"📊 *Бонус:* {bonus_text}\n\n"
        f"⸻\n\n"
        f"*Таблица начисления Монет:*\n\n"
        f"• 5 000💵 = 5🍀\n"
        f"• 10 000💵 = 10🍀\n"
        f"• 30 000💵 = 30🍀\n"
        f"• 60 000💵 = 60🍀\n"
        f"• 100 000💵 = 100🍀\n"
        f"• Далее — 1🍀 за каждую 1 000💵\n\n"
        f"⸻\n\n"
        f"*Как это работает:*\n"
        f"1. Совершайте покупки в магазине\n"
        f"2. После подтверждения заказа автоматически начисляются Монеты\n"
        f"3. Накапливайте Монеты и обменивайте их на товары\n"
        f"4. После каждого нового вайпа баланс обнуляется\n\n"
        f"💡 *Совет:* Чем выше ваш статус, тем больше бонусов!"
    )
    
    return message

def _get_or_create_user(user_id: int, username: str, full_name: str):
    user_data = get_user(user_id)
    if not user_data:
        create_user(user_id=user_id, username=username, first_name=full_name)
        user_data = get_user(user_id)
    return user_data

@router.message(F.text == "❤️ Кэшбэк")
async def show_cashback(message: Message):
    """Показывает информацию о кэшбэке"""
    user_data = _get_or_create_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.full_name
    )
    status = get_user_status(user_data['total_purchases'] or 0)
    total_coins = await get_combined_coins(message.from_user.id, user_data['coins_balance'] or 0)
    
    buttons = [
        [InlineKeyboardButton(text="🛍 Перейти в магазин", callback_data="shop")],
        [InlineKeyboardButton(text="👤 Личный кабинет", callback_data="profile")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await message.answer(
        get_cashback_info_message(status, total_coins),
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "cashback")
async def show_cashback_callback(callback: CallbackQuery):
    """Показывает информацию о кэшбэке через callback"""
    user_data = _get_or_create_user(
        callback.from_user.id,
        callback.from_user.username,
        callback.from_user.full_name
    )
    status = get_user_status(user_data['total_purchases'] or 0)
    total_coins = await get_combined_coins(callback.from_user.id, user_data['coins_balance'] or 0)
    
    buttons = [
        [InlineKeyboardButton(text="🛍 Перейти в магазин", callback_data="shop")],
        [InlineKeyboardButton(text="👤 Личный кабинет", callback_data="profile")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback.message.edit_text(
        get_cashback_info_message(status, total_coins),
        reply_markup=keyboard,
        parse_mode="Markdown"
    )