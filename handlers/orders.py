# handlers/orders.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime

from database.orders_db import get_user_orders, get_order_items
from database.users_db import get_user

router = Router()

def format_order_status(status: str) -> str:
    """Форматирует статус заказа"""
    statuses = {
        'pending': '🟡 Ожидает проверки',
        'confirmed': '🟢 Выполнен',
        'completed': '🟢 Выполнен',
        'cancelled': '🔴 Отклонён',
        'rejected': '🔴 Отклонён'
    }
    return statuses.get(status, '❓ Неизвестно')

def format_order_date(date_str: str) -> str:
    """Форматирует дату заказа"""
    try:
        date_obj = datetime.fromisoformat(date_str)
        return date_obj.strftime("%d.%m.%Y в %H:%M")
    except:
        return str(date_str)

def get_orders_keyboard(page: int = 0, total_pages: int = 1) -> InlineKeyboardMarkup:
    """Клавиатура для навигации по заказам"""
    buttons = []
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="◀️ Назад", callback_data=f"orders_page_{page-1}"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton(text="Вперед ▶️", callback_data=f"orders_page_{page+1}"))
    
    if nav_buttons:
        buttons.append(nav_buttons)
    
    buttons.append([InlineKeyboardButton(text="👤 Личный кабинет", callback_data="profile")])
    buttons.append([InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def format_orders_list(orders: list, page: int = 0, per_page: int = 5) -> tuple:
    """Форматирует список заказов с пагинацией"""
    if not orders:
        return "📦 Мои заказы\n\nУ вас пока нет заказов.", 0
    
    total_pages = (len(orders) + per_page - 1) // per_page
    start_idx = page * per_page
    end_idx = start_idx + per_page
    page_orders = orders[start_idx:end_idx]
    
    message_text = f"📦 Мои заказы\n\n"
    message_text += f"Всего заказов: {len(orders)}\n"
    message_text += f"Страница {page + 1} из {total_pages}\n\n"
    message_text += "⸻\n\n"
    
    for order in page_orders:
        order_items = get_order_items(order['order_id'])
        items_text = ", ".join([f"{item['product_name']} x{item['quantity']}" for item in order_items])
        
        message_text += (
            f"Заказ #{order['order_id']}\n"
            f"📅 Дата: {format_order_date(order['created_at'])}\n"
            f"🛒 Товары: {items_text}\n"
            f"💰 Сумма: {order['total_amount']}💵\n"
            f"💳 Оплата: {order['payment_method'] or 'Не указана'}\n"
            f"📊 Статус: {format_order_status(order['status'])}\n"
            f"🍀 Кэшбэк: {order['coins_earned']} 🪙\n"
        )
        
        if order['discount'] > 0:
            message_text += f"🎁 Скидка: {order['discount']}💵\n"
        if order['server']:
            message_text += f"🌍 Сервер: {order['server']}\n"
        if order['nickname']:
            message_text += f"👤 Ник: {order['nickname']}\n"
        
        message_text += "\n⸻\n\n"
    
    return message_text, total_pages

@router.message(F.text == "📦 Мои заказы")
async def show_orders(message: Message):
    """Показывает историю заказов"""
    user_data = get_user(message.from_user.id)
    
    if not user_data:
        await message.answer("❌ Пользователь не найден. Используйте /start")
        return
    
    orders = get_user_orders(message.from_user.id)
    message_text, total_pages = format_orders_list(orders)
    
    await message.answer(
        message_text,
        reply_markup=get_orders_keyboard(0, total_pages)
    )

@router.callback_query(F.data == "orders")
async def show_orders_callback(callback: CallbackQuery):
    """Показывает заказы через callback"""
    orders = get_user_orders(callback.from_user.id)
    message_text, total_pages = format_orders_list(orders)
    
    await callback.message.edit_text(
        message_text,
        reply_markup=get_orders_keyboard(0, total_pages)
    )

@router.callback_query(F.data.startswith("orders_page_"))
async def orders_page_callback(callback: CallbackQuery):
    """Переключение страниц заказов"""
    page = int(callback.data.replace("orders_page_", ""))
    orders = get_user_orders(callback.from_user.id)
    message_text, total_pages = format_orders_list(orders, page)
    
    await callback.message.edit_text(
        message_text,
        reply_markup=get_orders_keyboard(page, total_pages)
    )

@router.callback_query(F.data.startswith("order_detail_"))
async def show_order_detail(callback: CallbackQuery):
    """Показывает детальную информацию о заказе"""
    order_id = int(callback.data.replace("order_detail_", ""))
    orders = get_user_orders(callback.from_user.id)
    
    order = next((o for o in orders if o['order_id'] == order_id), None)
    
    if not order:
        await callback.answer("Заказ не найден")
        return
    
    order_items = get_order_items(order_id)
    
    message_text = (
        f"📦 Заказ #{order['order_id']}\n\n"
        f"📅 Дата: {format_order_date(order['created_at'])}\n"
        f"📊 Статус: {format_order_status(order['status'])}\n\n"
        f"Товары:\n"
    )
    
    for item in order_items:
        message_text += f"• {item['product_name']} x{item['quantity']} = {item['price'] * item['quantity']}💵\n"
    
    message_text += (
        f"\n💰 Сумма: {order['total_amount']}💵\n"
        f"🎁 Скидка: {order['discount']}💵\n"
        f"💳 Способ оплаты: {order['payment_method'] or 'Не указан'}\n"
        f"🍀 Кэшбэк: {order['coins_earned']} 🪙\n"
    )
    
    if order['server']:
        message_text += f"🌍 Сервер: {order['server']}\n"
    if order['nickname']:
        message_text += f"👤 Ник: {order['nickname']}\n"
    
    buttons = [
        [InlineKeyboardButton(text="🔙 К списку заказов", callback_data="orders")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback.message.edit_text(
        message_text,
        reply_markup=keyboard
    )