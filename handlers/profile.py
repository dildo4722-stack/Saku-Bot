# handlers/profile.py (исправленный)

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards.profile_keyboards import get_profile_keyboard, get_status_info_keyboard
from database.users_db import get_user, update_user, get_user_status
from database.supabase_client import get_combined_coins

router = Router()

class ProfileStates(StatesGroup):
    waiting_for_nickname = State()
    waiting_for_server = State()

def format_profile_message(user_data: dict, total_coins: int = None) -> str:
    """Форматирует сообщение с профилем пользователя"""
    if not user_data:
        return "❌ Пользователь не найден\nПожалуйста, перезапустите бота командой /start"
    
    status = get_user_status(user_data['total_purchases'] or 0)
    coins_to_show = total_coins if total_coins is not None else (user_data['coins_balance'] or 0)
    
    message = (
        f"👤 Личный кабинет\n\n"
        f"👤 Ник: {user_data['nickname'] or 'Не указан'}\n"
        f"🆔 Telegram ID: {user_data['user_id']}\n"
        f"🌍 Сервер: {user_data['server'] or 'Не указан'}\n"
        f"👑 Статус: {status['emoji']} {status['name']}\n"
        f"🍀 Баланс Монет: {coins_to_show} 🪙\n"
        f"💰 Общая сумма покупок: {user_data['total_purchases'] or 0}💵\n"
        f"📦 Количество заказов: {user_data['orders_count'] or 0}\n"
        f"👥 Приглашено друзей: {user_data['referrals_count'] or 0}\n"
        f"📅 Дата регистрации: {user_data['registration_date'] or 'Неизвестно'}\n"
        f"\n⸻\n"
        f"Преимущества статуса:\n"
    )
    
    benefits = {
        "👑 Легенда Sakura": [
            "Золотой значок", "+20% к кэшбэку", "Персональные скидки",
            "Отображение в ТОП покупателей", "Максимальный приоритет обработки заказов"
        ],
        "💎 VIP Клиент": [
            "Значок 💎", "+10% к начисляемым Монетам", "Персональные акции", "Закрытые розыгрыши"
        ],
        "🌸 Постоянный клиент": [
            "Значок 🌸", "Ранний доступ к акциям", "Приоритетная проверка заказов"
        ],
        "🌱 Новичок": [
            "Стандартный кэшбэк", "Участие в акциях"
        ]
    }
    
    for benefit in benefits.get(status['name'], []):
        message += f"• {benefit}\n"
    
    return message

@router.message(F.text == "👤 Личный кабинет")
async def show_profile(message: Message):
    """Показывает личный кабинет"""
    user_data = get_user(message.from_user.id)
    
    if not user_data:
        from database.users_db import create_user
        create_user(
            user_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )
        user_data = get_user(message.from_user.id)
    
    total_coins = await get_combined_coins(message.from_user.id, user_data['coins_balance'] or 0)
    await message.answer(
        format_profile_message(user_data, total_coins),
        reply_markup=get_profile_keyboard()
    )

@router.callback_query(F.data == "profile")
async def show_profile_callback(callback: CallbackQuery):
    """Показывает личный кабинет через callback"""
    user_data = get_user(callback.from_user.id)
    
    if not user_data:
        await callback.answer("Пользователь не найден. Используйте /start")
        return
    
    total_coins = await get_combined_coins(callback.from_user.id, user_data['coins_balance'] or 0)
    await callback.message.edit_text(
        format_profile_message(user_data, total_coins),
        reply_markup=get_profile_keyboard()
    )

@router.callback_query(F.data == "edit_nickname")
async def edit_nickname(callback: CallbackQuery, state: FSMContext):
    """Запрос на изменение ника"""
    await callback.message.edit_text("✏️ Введите ваш игровой ник:")
    await state.set_state(ProfileStates.waiting_for_nickname)
    await callback.answer()

@router.message(ProfileStates.waiting_for_nickname)
async def process_nickname(message: Message, state: FSMContext):
    """Обработка нового ника"""
    nickname = message.text
    update_user(message.from_user.id, nickname=nickname)
    await state.clear()
    
    user_data = get_user(message.from_user.id)
    total_coins = await get_combined_coins(message.from_user.id, user_data['coins_balance'] or 0)
    await message.answer(f"✅ Ник успешно изменен на: {nickname}")
    await message.answer(
        format_profile_message(user_data, total_coins),
        reply_markup=get_profile_keyboard()
    )

@router.callback_query(F.data == "edit_server")
async def edit_server(callback: CallbackQuery, state: FSMContext):
    """Запрос на изменение сервера"""
    await callback.message.edit_text("🌍 Выберите ваш сервер:\n\nОтправьте номер сервера (1-4)")
    await state.set_state(ProfileStates.waiting_for_server)
    await callback.answer()

@router.message(ProfileStates.waiting_for_server)
async def process_server(message: Message, state: FSMContext):
    """Обработка нового сервера"""
    server = message.text.strip()
    
    if server in ["1", "2", "3", "4"]:
        server_name = f"Сервер {server}"
        update_user(message.from_user.id, server=server_name)
        await state.clear()
        
        user_data = get_user(message.from_user.id)
        total_coins = await get_combined_coins(message.from_user.id, user_data['coins_balance'] or 0)
        await message.answer(f"✅ Сервер успешно изменен на: {server_name}")
        await message.answer(
            format_profile_message(user_data, total_coins),
            reply_markup=get_profile_keyboard()
        )
    else:
        await message.answer("❌ Неверный номер сервера.\nПожалуйста, введите число от 1 до 4.")

@router.callback_query(F.data == "status_details")
async def show_status_details(callback: CallbackQuery):
    """Показывает подробную информацию о статусах"""
    status_text = (
        "📊 Статусы покупателей\n\n"
        "🌱 Новичок\n"
        "От 0 до 49 999💵\n"
        "Даёт:\n"
        "• Стандартный кэшбэк\n"
        "• Участие в акциях\n\n"
        "🌸 Постоянный клиент\n"
        "От 50 000💵\n"
        "Даёт:\n"
        "• Значок 🌸\n"
        "• Ранний доступ к акциям\n"
        "• Приоритетную проверку заказов\n\n"
        "💎 VIP Клиент\n"
        "От 150 000💵\n"
        "Даёт:\n"
        "• Значок 💎\n"
        "• +10% к начисляемым Монетам\n"
        "• Персональные акции\n"
        "• Закрытые розыгрыши\n\n"
        "👑 Легенда Sakura\n"
        "От 400 000💵\n"
        "Даёт:\n"
        "• Золотой значок\n"
        "• +20% к кэшбэку\n"
        "• Персональные скидки\n"
        "• Отображение в ТОП покупателей\n"
        "• Максимальный приоритет обработки заказов\n\n"
        "⸻\n"
        "Статус зависит от общей суммы покупок."
    )
    
    await callback.message.edit_text(
        status_text,
        reply_markup=get_status_info_keyboard()
    )

@router.callback_query(F.data == "purchase_history")
async def show_purchase_history(callback: CallbackQuery):
    """Показывает историю покупок"""
    from database.orders_db import get_user_orders
    
    orders = get_user_orders(callback.from_user.id)
    
    if not orders:
        history_text = "📦 История покупок\n\nУ вас пока нет заказов."
    else:
        total_amount = sum(order['total_amount'] for order in orders)
        history_text = (
            f"📦 История покупок\n\n"
            f"Всего заказов: {len(orders)}\n"
            f"Общая сумма: {total_amount}💵\n\n"
            f"Последние заказы:\n"
        )
        
        for order in orders[:5]:
            status_emoji = {'pending': '⏳', 'confirmed': '✅', 'completed': '✨', 'cancelled': '❌'}
            emoji = status_emoji.get(order['status'], '❓')
            history_text += f"{emoji} Заказ #{order['order_id']} - {order['total_amount']}💵\n"
    
    buttons = [
        [InlineKeyboardButton(text="🔙 Назад в профиль", callback_data="profile")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback.message.edit_text(history_text, reply_markup=keyboard)