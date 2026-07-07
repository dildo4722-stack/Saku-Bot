# handlers/cashback.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from data.users import get_user_data

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
    
    # Проверяем точные совпадения
    if amount in cashback_rates:
        return cashback_rates[amount]
    
    # Если сумма больше 100000
    if amount > 100000:
        # Базовые 100 монет за первые 100000
        coins = 100
        # +1 монета за каждую 1000 сверх 100000
        extra_amount = amount - 100000
        coins += extra_amount // 1000
        return coins
    
    # Если сумма между ставками
    if amount > 60000:
        return 60
    elif amount > 30000:
        return 30
    elif amount > 10000:
        return 10
    elif amount > 5000:
        return 5
    else:
        # Для сумм меньше 5000 - 1 монета за каждую 1000
        return amount // 1000

def get_cashback_info_message(user_data: dict) -> str:
    """Формирует сообщение с информацией о кэшбэке"""
    status = user_data["status"]
    
    # Определяем бонус к кэшбэку в зависимости от статуса
    cashback_bonus = 0
    if status["name"] == "👑 Легенда Sakura":
        cashback_bonus = 20
        bonus_text = "+20% к кэшбэку"
    elif status["name"] == "💎 VIP Клиент":
        cashback_bonus = 10
        bonus_text = "+10% к Монетам"
    else:
        bonus_text = "Стандартный кэшбэк"
    
    message = (
        f"💰 *Кэшбэк*\n\n"
        f"🍀 *Ваш баланс Монет:* {user_data['coins_balance']} 🍀\n"
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

@router.message(F.text == "❤️ Кэшбэк")
async def show_cashback(message: Message):
    """Показывает информацию о кэшбэке"""
    user_data = get_user_data(
        message.from_user.id,
        message.from_user.username or message.from_user.full_name
    )
    
    buttons = [
        [InlineKeyboardButton(text="🛍 Перейти в магазин", callback_data="shop")],
        [InlineKeyboardButton(text="👤 Личный кабинет", callback_data="profile")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await message.answer(
        get_cashback_info_message(user_data),
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "cashback")
async def show_cashback_callback(callback: CallbackQuery):
    """Показывает информацию о кэшбэке через callback"""
    user_data = get_user_data(
        callback.from_user.id,
        callback.from_user.username or callback.from_user.full_name
    )
    
    buttons = [
        [InlineKeyboardButton(text="🛍 Перейти в магазин", callback_data="shop")],
        [InlineKeyboardButton(text="👤 Личный кабинет", callback_data="profile")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback.message.edit_text(
        get_cashback_info_message(user_data),
        reply_markup=keyboard,
        parse_mode="Markdown"
    )