# handlers/admin_full.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime
import os
import shutil

from database.db import get_connection
from database.admin_db import (
    is_admin, get_all_orders, get_order_by_id, update_order_status,
    delete_order, get_all_users, get_user_by_id, update_user_admin,
    delete_user_admin, get_statistics, reset_all_coins, reset_referrals
)
from database.orders_db import get_order_items, get_user_orders
from database.admin_logs import add_log, get_logs
from database.admin_settings import get_setting, set_setting, init_settings
from database.promocodes_db import check_promocode
from data.products import PRODUCTS, get_product_by_id

router = Router()

class AdminStates(StatesGroup):
    waiting_for_broadcast = State()
    waiting_for_broadcast_media = State()
    waiting_for_news_title = State()
    waiting_for_news_content = State()
    waiting_for_news_media = State()
    waiting_for_product_name = State()
    waiting_for_product_desc = State()
    waiting_for_product_price = State()
    waiting_for_product_stars = State()
    waiting_for_product_category = State()
    waiting_for_edit_product_field = State()
    waiting_for_edit_product_value = State()
    waiting_for_promocode_code = State()
    waiting_for_promocode_discount = State()
    waiting_for_promocode_max_uses = State()
    waiting_for_promocode_min_amount = State()
    waiting_for_promocode_valid_until = State()
    waiting_for_setting_key = State()
    waiting_for_setting_value = State()
    waiting_for_user_search = State()
    waiting_for_user_coins = State()
    waiting_for_wipe_confirm = State()
    waiting_for_setting_value = State()
    waiting_for_promocode_code = State()
    waiting_for_promocode_discount = State()
    waiting_for_promocode_max_uses = State()
    waiting_for_promocode_min_amount = State()
    waiting_for_promocode_category = State()
    waiting_for_promocode_valid_until = State()

# ========== ГЛАВНОЕ МЕНЮ АДМИНА ==========

def get_admin_inline_menu() -> InlineKeyboardMarkup:
    """Инлайн меню админа"""
    return InlineKeyboardMarkup(inline_keyboard=[
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
    ])

@router.message(F.text == "🏠 Обычное меню")
async def switch_to_user_menu(message: Message):
    from handlers.start import send_welcome_page
    await send_welcome_page(message)

@router.callback_query(F.data == "admin_menu")
async def admin_menu(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return await callback.answer("❌ Нет доступа")
    await callback.message.edit_text("🔑 Админ-панель SAKURA STORE\n\nВыберите раздел:", 
                                  reply_markup=get_admin_inline_menu())


# ========== ЗАКАЗЫ ==========

@router.message(F.text == "📦 Заказы")
@router.callback_query(F.data == "admin_orders")
async def admin_orders(event: Message | CallbackQuery, status: str = None):
    if isinstance(event, CallbackQuery):
        if not is_admin(event.from_user.id): return await event.answer("❌ Нет доступа")
        msg = event.message
        is_cb = True
    else:
        if not is_admin(event.from_user.id): return
        msg = event
        is_cb = False
    
    orders = get_all_orders(status=status) if status else get_all_orders()
    
    if not orders:
        text = "📦 Заказов нет"
    else:
        counts = {}
        for o in get_all_orders(): counts[o['status']] = counts.get(o['status'], 0) + 1
        
        text = f"📦 Заказы\n🟡 {counts.get('pending', 0)} 🟢 {counts.get('completed', 0)} 🔴 {counts.get('rejected', 0)}\n\n"
        
        for order in orders[:15]:
            items = get_order_items(order['order_id'])
            items_text = ", ".join([f"{i['product_name']} x{i['quantity']}" for i in items])
            emoji = {'pending': '🟡', 'completed': '🟢', 'rejected': '🔴'}.get(order['status'], '❓')
            text += f"{emoji} #{order['order_id']} | {order['first_name'] or order['username']}\n🛒 {items_text}\n💰 {order['total_amount']}💵\n👉 /order_{order['order_id']}\n\n"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🟡 Новые", callback_data="admin_orders_pending"),
         InlineKeyboardButton(text="🟢 Готовые", callback_data="admin_orders_completed"),
         InlineKeyboardButton(text="🔴 Отказ", callback_data="admin_orders_rejected")],
        [InlineKeyboardButton(text="📋 Все", callback_data="admin_orders_all")],
        [InlineKeyboardButton(text="🔙 Меню", callback_data="admin_menu")]
    ])
    
    if is_cb:
        # Если сообщение с фото - отправляем новое
        try:
            await msg.edit_text(text, reply_markup=kb)
        except:
            await msg.answer(text, reply_markup=kb)
    else:
        await msg.answer(text, reply_markup=kb)

@router.callback_query(F.data.startswith("admin_orders_"))
async def admin_orders_filter(callback: CallbackQuery):
    filter_map = {'pending': 'pending', 'completed': 'completed', 'rejected': 'rejected', 'all': None}
    status = callback.data.replace("admin_orders_", "")
    await admin_orders(callback, status=filter_map.get(status))

@router.message(F.text.startswith("/order_"))
async def order_detail_command(message: Message):
    if not is_admin(message.from_user.id): return
    try:
        order_id = int(message.text.replace("/order_", ""))
        order = get_order_by_id(order_id)
        if not order:
            await message.answer("❌ Заказ не найден")
            return
        
        items = get_order_items(order_id)
        items_text = "\n".join([f"• {i['product_name']} x{i['quantity']} = {i['price']*i['quantity']}💵" for i in items])
        status_emoji = {'pending': '🟡', 'completed': '🟢', 'rejected': '🔴'}.get(order['status'], '❓')
        
        text = (
            f"📦 Заказ #{order['order_id']}\n\n"
            f"📅 {order['created_at'][:19]}\n"
            f"👤 {order['first_name'] or '—'} (@{order['username'] or '—'})\n"
            f"🆔 {order['user_id']}\n"
            f"🎮 Ник: {order['nickname'] or '—'}\n"
            f"🌍 Сервер: {order['server'] or '—'}\n\n"
            f"Товары:\n{items_text}\n\n"
            f"💰 Сумма: {order['total_amount']}💵\n"
            f"💳 Оплата: {order['payment_method'] or '—'}\n"
            f"🎁 Скидка: {order['discount']}💵\n"
            f"🍀 Кэшбэк: {order['coins_earned']} 🪙\n"
            f"📊 Статус: {status_emoji} {order['status']}"
        )
        
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"admin_confirm_{order_id}"),
             InlineKeyboardButton(text="❌ Отклонить", callback_data=f"admin_reject_menu_{order_id}")],
            [InlineKeyboardButton(text="🗑 Удалить", callback_data=f"admin_delete_order_{order_id}")],
            [InlineKeyboardButton(text="🔙 К заказам", callback_data="admin_orders")]
        ])
        
        # Если есть скриншот - отправляем фото с текстом
        if order.get('screenshot_id'):
            await message.answer_photo(
                photo=order['screenshot_id'],
                caption=text,
                reply_markup=kb
            )
        else:
            await message.answer(text, reply_markup=kb)
            
    except:
        await message.answer("❌ Неверный формат. Используйте /order_ID")

@router.callback_query(F.data.startswith("admin_confirm_"))
async def admin_confirm(callback: CallbackQuery):
    order_id = int(callback.data.replace("admin_confirm_", ""))
    update_order_status(order_id, "completed", callback.from_user.id)
    order = get_order_by_id(order_id)
    
    if order:
        reviews_chat = get_setting("reviews_chat", "")
        
        # Базовое сообщение БЕЗ Markdown
        confirm_text = "🌸 Ваш заказ подтверждён!\n\nСпасибо за покупку!\nОжидайте выдачу товара."
        
        if reviews_chat:
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="⭐ Оставить отзыв", url=reviews_chat)]
            ])
            try:
                await callback.bot.send_message(
                    order['user_id'], 
                    confirm_text + "\n\n💬 Будем рады вашему отзыву!",
                    reply_markup=kb
                )
            except:
                try:
                    await callback.bot.send_message(order['user_id'], confirm_text)
                except:
                    pass
        else:
            try:
                await callback.bot.send_message(order['user_id'], confirm_text)
            except:
                pass
    
    add_log("order_confirm", callback.from_user.id, f"Заказ #{order_id} подтверждён")
    await callback.answer("✅ Подтверждён")
    await admin_orders(callback)



@router.callback_query(F.data.startswith("admin_reject_menu_"))
async def admin_reject_menu(callback: CallbackQuery):
    order_id = int(callback.data.replace("admin_reject_menu_", ""))
    reasons = [("Неверный чек", "wrong_receipt"), ("Недостаточная сумма", "insufficient_amount"),
               ("Оплата не найдена", "payment_not_found"), ("Неверный сервер", "wrong_server"), ("Другое", "other")]
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t, callback_data=f"admin_reject_{order_id}_{r}")] for t, r in reasons
    ] + [[InlineKeyboardButton(text="🔙 Назад", callback_data=f"admin_order_{order_id}")]])
    await callback.message.edit_text("❌ Выберите причину:", reply_markup=kb)

@router.callback_query(F.data.startswith("admin_reject_"))
async def admin_reject(callback: CallbackQuery):
    parts = callback.data.split("_")
    order_id = int(parts[2])
    reason = "_".join(parts[3:])
    reasons = {"wrong_receipt": "Неверный чек", "insufficient_amount": "Недостаточная сумма",
               "payment_not_found": "Оплата не найдена", "wrong_server": "Неверный сервер", "other": "Другое"}
    update_order_status(order_id, "rejected", callback.from_user.id)
    order = get_order_by_id(order_id)
    if order:
        try: 
            # БЕЗ parse_mode="Markdown"
            await callback.bot.send_message(
                order['user_id'], 
                f"❌ Заказ #{order_id} отклонён\n\nПричина: {reasons.get(reason, reason)}\n\nСвяжитесь с поддержкой."
            )
        except: pass
    add_log("order_reject", callback.from_user.id, f"Заказ #{order_id} отклонён: {reasons.get(reason, '')}")
    await callback.answer("❌ Отклонён")
    await admin_orders(callback)

@router.callback_query(F.data.startswith("admin_delete_order_"))
async def admin_delete_order(callback: CallbackQuery):
    order_id = int(callback.data.replace("admin_delete_order_", ""))
    delete_order(order_id)
    add_log("order_delete", callback.from_user.id, f"Заказ #{order_id} удалён")
    await callback.answer("🗑 Удалён")
    await admin_orders(callback)

@router.callback_query(F.data.startswith("admin_order_"))
async def admin_order_view(callback: CallbackQuery):
    order_id = int(callback.data.replace("admin_order_", ""))
    order = get_order_by_id(order_id)
    if not order:
        await callback.answer("Не найден")
        return
    
    items = get_order_items(order_id)
    items_text = "\n".join([f"• {i['product_name']} x{i['quantity']} = {i['price']*i['quantity']}💵" for i in items])
    text = f"📦 Заказ #{order_id}\n\n👤 {order['first_name']} | 💰 {order['total_amount']}💵\n📊 {order['status']}\n\n{items_text}"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"admin_confirm_{order_id}"),
         InlineKeyboardButton(text="❌ Отклонить", callback_data=f"admin_reject_menu_{order_id}")],
        [InlineKeyboardButton(text="🗑 Удалить", callback_data=f"admin_delete_order_{order_id}")],
        [InlineKeyboardButton(text="🔙 К заказам", callback_data="admin_orders")]
    ])
    
    # Всегда отправляем новое сообщение вместо редактирования
    if order.get('screenshot_id'):
        await callback.message.answer_photo(
            photo=order['screenshot_id'],
            caption=text,
            reply_markup=kb
        )
    else:
        await callback.message.answer(text, reply_markup=kb)
    
    await callback.answer()

# ========== ПОЛЬЗОВАТЕЛИ ==========

@router.message(F.text == "👥 Пользователи")
@router.callback_query(F.data == "admin_users")
async def admin_users(event: Message | CallbackQuery):
    if isinstance(event, CallbackQuery):
        if not is_admin(event.from_user.id): return await event.answer("❌ Нет доступа")
        msg, is_cb = event.message, True
    else:
        if not is_admin(event.from_user.id): return
        msg, is_cb = event, False
    
    users = get_all_users()
    text = f"👥 *Пользователи* ({len(users)})\n\n"
    for u in users[:30]:
        text += f"• {u['first_name'] or '—'} | `{u['user_id']}` | 💰{u['total_purchases'] or 0}💵 | 🍀{u['coins_balance'] or 0}\n"
    text += "\n🔍 /user_ID — детали"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Меню", callback_data="admin_menu")]])
    if is_cb: await msg.edit_text(text, reply_markup=kb)
    else: await msg.answer(text, reply_markup=kb)

@router.message(F.text.startswith("/user_"))
async def user_detail(message: Message):
    if not is_admin(message.from_user.id): return
    try:
        user_id = int(message.text.replace("/user_", ""))
        user = get_user_by_id(user_id)
        if not user:
            await message.answer("❌ Пользователь не найден")
            return
        
        status = get_user_status_admin(user['total_purchases'] or 0)
        orders = get_user_orders(user_id)
        
        text = (
            f"👤 *Профиль пользователя*\n\n"
            f"👤 Имя: {user['first_name'] or '—'}\n"
            f"📛 Username: @{user['username'] or '—'}\n"
            f"🆔 ID: `{user['user_id']}`\n"
            f"🎮 Ник: {user['nickname'] or '—'}\n"
            f"🌍 Сервер: {user['server'] or '—'}\n"
            f"📅 Регистрация: {user['registration_date']}\n"
            f"👑 Статус: {status['name']}\n"
            f"📦 Заказов: {user['orders_count'] or 0}\n"
            f"💰 Покупок: {user['total_purchases'] or 0}💵\n"
            f"🍀 Монет: {user['coins_balance'] or 0} 🪙\n"
            f"👥 Рефералов: {user['referrals_count'] or 0}\n"
            f"🚫 Заблокирован: {'Да' if user.get('is_blocked') else 'Нет'}\n"
        )
        
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🍀 Монеты +/-", callback_data=f"admin_user_coins_{user_id}"),
             InlineKeyboardButton(text="🚫 Блок", callback_data=f"admin_user_block_{user_id}")],
            [InlineKeyboardButton(text="🗑 Удалить", callback_data=f"admin_user_delete_{user_id}")],
            [InlineKeyboardButton(text="🔙 К списку", callback_data="admin_users")]
        ])
        
        await message.answer(text, reply_markup=kb)
    except:
        await message.answer("❌ Формат: /user_ID")

def get_user_status_admin(total: int) -> dict:
    if total >= 400000: return {"name": "👑 Легенда Sakura"}
    elif total >= 150000: return {"name": "💎 VIP Клиент"}
    elif total >= 50000: return {"name": "🌸 Постоянный клиент"}
    return {"name": "🌱 Новичок"}

@router.callback_query(F.data.startswith("admin_user_block_"))
async def admin_user_block(callback: CallbackQuery):
    user_id = int(callback.data.replace("admin_user_block_", ""))
    user = get_user_by_id(user_id)
    new_status = not user.get('is_blocked')
    update_user_admin(user_id, is_blocked=new_status)
    add_log("user_block", callback.from_user.id, f"Пользователь {user_id} {'заблокирован' if new_status else 'разблокирован'}")
    await callback.answer(f"{'🚫 Заблокирован' if new_status else '✅ Разблокирован'}")
    await admin_users(callback)

@router.callback_query(F.data.startswith("admin_user_delete_"))
async def admin_user_delete(callback: CallbackQuery):
    user_id = int(callback.data.replace("admin_user_delete_", ""))
    delete_user_admin(user_id)
    add_log("user_delete", callback.from_user.id, f"Пользователь {user_id} удалён")
    await callback.answer("🗑 Удалён")
    await admin_users(callback)

@router.callback_query(F.data.startswith("admin_user_coins_"))
async def admin_user_coins(callback: CallbackQuery, state: FSMContext):
    user_id = int(callback.data.replace("admin_user_coins_", ""))
    await state.update_data(edit_user_id=user_id)
    await callback.message.edit_text(f"🍀 Изменить баланс Монет\n\nПользователь ID: {user_id}\nТекущий баланс: {get_user_by_id(user_id)['coins_balance'] or 0} 🪙\n\nОтправьте число (например +100 или -50):")
    await state.set_state(AdminStates.waiting_for_user_coins)
    await callback.answer()

@router.message(AdminStates.waiting_for_user_coins)
async def process_user_coins(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = data['edit_user_id']
    try:
        amount = int(message.text)
        user = get_user_by_id(user_id)
        new_balance = (user['coins_balance'] or 0) + amount
        if new_balance < 0: new_balance = 0
        update_user_admin(user_id, coins_balance=new_balance)
        add_log("coins_edit", message.from_user.id, f"Баланс {user_id}: {amount} (теперь {new_balance})")
        await message.answer(f"✅ Баланс изменён: {new_balance} 🪙")
    except:
        await message.answer("❌ Неверное число")
    await state.clear()

# ========== ТОВАРЫ ==========

# handlers/admin_full.py (заменить блок ТОВАРЫ)

# ========== ТОВАРЫ ==========

@router.message(F.text == "🛍 Товары")
@router.callback_query(F.data == "admin_products")
async def admin_products(event: Message | CallbackQuery):
    if isinstance(event, CallbackQuery):
        if not is_admin(event.from_user.id): return await event.answer("❌ Нет доступа")
        msg, is_cb = event.message, True
    else:
        if not is_admin(event.from_user.id): return
        msg, is_cb = event, False
    
    text = "🛍 *Управление товарами*\n\n"
    for category, products in PRODUCTS.items():
        visible = sum(1 for p in products if p.get('is_available', True))
        text += f"*{category}:* {visible}/{len(products)} шт.\n"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить товар", callback_data="admin_product_add")],
        [InlineKeyboardButton(text="✏️ Изменить товар", callback_data="admin_product_edit_list")],
        [InlineKeyboardButton(text="👁 Скрыть/Показать", callback_data="admin_product_toggle_list")],
        [InlineKeyboardButton(text="🗑 Удалить товар", callback_data="admin_product_delete_list")],
        [InlineKeyboardButton(text="📂 Категории", callback_data="admin_categories")],
        [InlineKeyboardButton(text="🔙 Меню", callback_data="admin_menu")]
    ])
    
    if is_cb: await msg.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    else: await msg.answer(text, reply_markup=kb, parse_mode="Markdown")

# ========== ДОБАВИТЬ ТОВАР ==========

@router.callback_query(F.data == "admin_product_add")
async def admin_product_add(callback: CallbackQuery, state: FSMContext):
    """Добавление товара - шаг 1: категория"""
    categories = list(PRODUCTS.keys())
    buttons = []
    for cat in categories:
        buttons.append([InlineKeyboardButton(text=f"📂 {cat}", callback_data=f"add_product_cat_{cat}")])
    buttons.append([InlineKeyboardButton(text="➕ Новая категория", callback_data="add_product_new_cat")])
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="admin_products")])
    
    await callback.message.edit_text("Выберите категорию:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await callback.answer()

@router.callback_query(F.data.startswith("add_product_cat_"))
async def add_product_cat(callback: CallbackQuery, state: FSMContext):
    """Выбор категории - шаг 2: название"""
    category = callback.data.replace("add_product_cat_", "")
    await state.update_data(product_category=category)
    await callback.message.edit_text(f"Категория: {category}\n\nОтправьте *название товара*:")
    await state.set_state(AdminStates.waiting_for_product_name)
    await callback.answer()

@router.callback_query(F.data == "add_product_new_cat")
async def add_product_new_cat(callback: CallbackQuery, state: FSMContext):
    """Новая категория"""
    await callback.message.edit_text("Отправьте название новой категории:")
    await state.set_state(AdminStates.waiting_for_product_category)
    await state.update_data(is_new_category=True)
    await callback.answer()

@router.message(AdminStates.waiting_for_product_category)
async def process_new_category(message: Message, state: FSMContext):
    """Создание новой категории"""
    category = message.text.strip().lower()
    if category not in PRODUCTS:
        PRODUCTS[category] = []
    await state.update_data(product_category=category, is_new_category=False)
    await message.answer(f"Категория: {category}\n\nОтправьте *название товара*:")
    await state.set_state(AdminStates.waiting_for_product_name)

@router.message(AdminStates.waiting_for_product_name)
async def product_name(message: Message, state: FSMContext):
    """Название товара - шаг 3: описание"""
    await state.update_data(product_name=message.text.strip())
    await message.answer(f"Название: {message.text}\n\nОтправьте *описание товара* (или /skip):")
    await state.set_state(AdminStates.waiting_for_product_desc)

@router.message(AdminStates.waiting_for_product_desc)
async def product_desc(message: Message, state: FSMContext):
    """Описание товара - шаг 4: цена в валюте"""
    desc = "" if message.text == "/skip" else message.text.strip()
    await state.update_data(product_desc=desc)
    await message.answer(f"Описание: {desc or 'Нет'}\n\nОтправьте *цену в игровой валюте* (💵):")
    await state.set_state(AdminStates.waiting_for_product_price)

@router.message(AdminStates.waiting_for_product_price)
async def product_price(message: Message, state: FSMContext):
    """Цена в валюте - шаг 5: цена в Stars"""
    try:
        price = int(message.text)
        if price < 0:
            await message.answer("❌ Цена не может быть отрицательной")
            return
        await state.update_data(product_price=price)
        await message.answer(f"Цена 💵: {price}\n\nОтправьте *цену в Telegram Stars* (⭐):")
        await state.set_state(AdminStates.waiting_for_product_stars)
    except:
        await message.answer("❌ Отправьте число")

@router.message(AdminStates.waiting_for_product_stars)
async def product_stars(message: Message, state: FSMContext):
    """Цена в Stars - сохранение товара"""
    try:
        stars = int(message.text)
        if stars < 0:
            await message.answer("❌ Цена не может быть отрицательной")
            return
        
        data = await state.get_data()
        
        # Генерируем новый ID
        max_id = 0
        for cat in PRODUCTS.values():
            for p in cat:
                if p['id'] > max_id:
                    max_id = p['id']
        new_id = max_id + 1
        
        new_product = {
            "id": new_id,
            "name": data['product_name'],
            "price_game": data['product_price'],
            "price_stars": stars,
            "description": data['product_desc'],
            "is_available": True
        }
        
        PRODUCTS[data['product_category']].append(new_product)
        
        add_log("product_add", message.from_user.id, f"Товар: {data['product_name']} ({data['product_category']})")
        
        await message.answer(
            f"✅ *Товар добавлен!*\n\n"
            f"📂 Категория: {data['product_category']}\n"
            f"📝 Название: {data['product_name']}\n"
            f"💵 Цена: {data['product_price']}💵\n"
            f"⭐ Stars: {stars}⭐\n"
            f"📋 ID: {new_id}"
        )
        await state.clear()
    except:
        await message.answer("❌ Отправьте число")

# ========== ИЗМЕНИТЬ ТОВАР ==========

@router.callback_query(F.data == "admin_product_edit_list")
async def admin_product_edit_list(callback: CallbackQuery):
    """Список товаров для изменения"""
    buttons = []
    for cat, products in PRODUCTS.items():
        for p in products:
            buttons.append([InlineKeyboardButton(
                text=f"{p['name']} ({cat})", 
                callback_data=f"edit_product_{p['id']}"
            )])
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="admin_products")])
    
    await callback.message.edit_text("✏️ Выберите товар для изменения:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await callback.answer()

@router.callback_query(F.data.startswith("edit_product_"))
async def edit_product_menu(callback: CallbackQuery):
    """Меню изменения товара"""
    product_id = int(callback.data.replace("edit_product_", ""))
    product = get_product_by_id(product_id)
    
    if not product:
        await callback.answer("Товар не найден")
        return
    
    text = (
        f"✏️ *Изменение товара*\n\n"
        f"ID: {product['id']}\n"
        f"Название: {product['name']}\n"
        f"Категория: {product.get('category', '—')}\n"
        f"💵 Цена: {product['price_game']}💵\n"
        f"⭐ Stars: {product['price_stars']}⭐\n"
        f"👁 Видим: {'Да' if product.get('is_available', True) else 'Нет'}\n\n"
        f"Что изменить?"
    )
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Название", callback_data=f"edit_field_name_{product_id}")],
        [InlineKeyboardButton(text="📋 Описание", callback_data=f"edit_field_desc_{product_id}")],
        [InlineKeyboardButton(text="💵 Цена 💵", callback_data=f"edit_field_price_{product_id}")],
        [InlineKeyboardButton(text="⭐ Цена ⭐", callback_data=f"edit_field_stars_{product_id}")],
        [InlineKeyboardButton(text="📂 Категория", callback_data=f"edit_field_cat_{product_id}")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_product_edit_list")]
    ])
    
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data.startswith("edit_field_"))
async def edit_field(callback: CallbackQuery, state: FSMContext):
    """Запрос нового значения поля"""
    parts = callback.data.split("_")
    field = parts[2]
    product_id = int(parts[3])
    
    field_names = {
        "name": "название",
        "desc": "описание",
        "price": "цену в 💵",
        "stars": "цену в ⭐",
        "cat": "категорию"
    }
    
    await state.update_data(edit_product_id=product_id, edit_field=field)
    await callback.message.edit_text(f"Отправьте новое {field_names.get(field, field)}:")
    await state.set_state(AdminStates.waiting_for_edit_product_value)
    await callback.answer()

@router.message(AdminStates.waiting_for_edit_product_value)
async def process_edit_value(message: Message, state: FSMContext):
    """Сохранение изменений"""
    data = await state.get_data()
    product_id = data['edit_product_id']
    field = data['edit_field']
    value = message.text.strip()
    
    # Находим товар
    product = None
    product_cat = None
    for cat, products in PRODUCTS.items():
        for p in products:
            if p['id'] == product_id:
                product = p
                product_cat = cat
                break
    
    if not product:
        await message.answer("❌ Товар не найден")
        await state.clear()
        return
    
    # Изменяем поле
    if field == "name":
        product['name'] = value
    elif field == "desc":
        product['description'] = value
    elif field == "price":
        try:
            product['price_game'] = int(value)
        except:
            await message.answer("❌ Отправьте число")
            return
    elif field == "stars":
        try:
            product['price_stars'] = int(value)
        except:
            await message.answer("❌ Отправьте число")
            return
    elif field == "cat":
        if value not in PRODUCTS:
            PRODUCTS[value] = []
        PRODUCTS[product_cat].remove(product)
        PRODUCTS[value].append(product)
    
    add_log("product_edit", message.from_user.id, f"Товар #{product_id}: {field} изменен")
    await message.answer(f"✅ Товар обновлен!")
    await state.clear()

# ========== СКРЫТЬ/ПОКАЗАТЬ ТОВАР ==========

@router.callback_query(F.data == "admin_product_toggle_list")
async def admin_product_toggle_list(callback: CallbackQuery):
    """Список для скрытия/показа"""
    buttons = []
    for cat, products in PRODUCTS.items():
        for p in products:
            emoji = "👁" if p.get('is_available', True) else "🚫"
            buttons.append([InlineKeyboardButton(
                text=f"{emoji} {p['name']} ({cat})",
                callback_data=f"toggle_product_{p['id']}"
            )])
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="admin_products")])
    
    await callback.message.edit_text("Выберите товар для скрытия/показа:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await callback.answer()

@router.callback_query(F.data.startswith("toggle_product_"))
async def toggle_product(callback: CallbackQuery):
    """Переключение видимости товара"""
    product_id = int(callback.data.replace("toggle_product_", ""))
    
    for cat, products in PRODUCTS.items():
        for p in products:
            if p['id'] == product_id:
                p['is_available'] = not p.get('is_available', True)
                status = "показан" if p['is_available'] else "скрыт"
                add_log("product_toggle", callback.from_user.id, f"Товар #{product_id}: {status}")
                await callback.answer(f"✅ Товар {status}")
                await admin_product_toggle_list(callback)
                return
    
    await callback.answer("Товар не найден")

# ========== УДАЛИТЬ ТОВАР ==========

@router.callback_query(F.data == "admin_product_delete_list")
async def admin_product_delete_list(callback: CallbackQuery):
    """Список для удаления"""
    buttons = []
    for cat, products in PRODUCTS.items():
        for p in products:
            buttons.append([InlineKeyboardButton(
                text=f"🗑 {p['name']} ({cat})",
                callback_data=f"delete_product_{p['id']}"
            )])
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="admin_products")])
    
    await callback.message.edit_text("🗑 Выберите товар для удаления:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await callback.answer()

@router.callback_query(F.data.startswith("delete_product_"))
async def delete_product(callback: CallbackQuery):
    """Удаление товара"""
    product_id = int(callback.data.replace("delete_product_", ""))
    
    for cat, products in PRODUCTS.items():
        for p in products:
            if p['id'] == product_id:
                products.remove(p)
                add_log("product_delete", callback.from_user.id, f"Товар #{product_id} удален")
                await callback.answer("🗑 Удален")
                await admin_product_delete_list(callback)
                return
    
    await callback.answer("Товар не найден")

# ========== КАТЕГОРИИ ==========

@router.callback_query(F.data == "admin_categories")
async def admin_categories(callback: CallbackQuery):
    """Управление категориями"""
    text = "📂 *Категории*\n\n"
    for cat, products in PRODUCTS.items():
        text += f"• {cat}: {len(products)} шт.\n"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Создать категорию", callback_data="admin_cat_add")],
        [InlineKeyboardButton(text="🗑 Удалить категорию", callback_data="admin_cat_delete_list")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_products")]
    ])
    
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "admin_cat_add")
async def admin_cat_add(callback: CallbackQuery, state: FSMContext):
    """Создание новой категории"""
    await callback.message.edit_text("Отправьте название новой категории:")
    await state.set_state(AdminStates.waiting_for_product_category)
    await state.update_data(is_new_category=True)
    await callback.answer()

@router.callback_query(F.data == "admin_cat_delete_list")
async def admin_cat_delete_list(callback: CallbackQuery):
    """Список категорий для удаления"""
    buttons = []
    for cat in PRODUCTS.keys():
        if PRODUCTS[cat]:  # Только пустые
            continue
        buttons.append([InlineKeyboardButton(text=f"🗑 {cat}", callback_data=f"delete_cat_{cat}")])
    
    if not buttons:
        await callback.answer("Нет пустых категорий для удаления")
        return
    
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="admin_categories")])
    await callback.message.edit_text("Выберите категорию для удаления (только пустые):", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await callback.answer()

@router.callback_query(F.data.startswith("delete_cat_"))
async def delete_category(callback: CallbackQuery):
    """Удаление категории"""
    cat = callback.data.replace("delete_cat_", "")
    if cat in PRODUCTS and not PRODUCTS[cat]:
        del PRODUCTS[cat]
        add_log("category_delete", callback.from_user.id, f"Категория: {cat}")
        await callback.answer(f"🗑 Категория {cat} удалена")
    else:
        await callback.answer("❌ Нельзя удалить (не пуста)")
    await admin_categories(callback)

# ========== ПРОМОКОДЫ ==========

@router.message(F.text == "🎟 Промокоды")
@router.callback_query(F.data == "admin_promocodes")
async def admin_promocodes(event: Message | CallbackQuery):
    if isinstance(event, CallbackQuery):
        msg, is_cb = event.message, True
    else:
        if not is_admin(event.from_user.id): return
        msg, is_cb = event, False
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM promocodes ORDER BY created_at DESC LIMIT 20")
    promos = cursor.fetchall()
    conn.close()
    
    text = "🎟 *Промокоды*\n\n"
    if promos:
        for p in promos:
            text += f"• `{p['code']}` | -{p['discount_percent']}% | {p['uses_count']}/{p['max_uses'] or '∞'}\n"
    else:
        text += "Нет промокодов\n\n"
    
    text += "\n📝 /add_promo — создать"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Меню", callback_data="admin_menu")]])
    if is_cb: await msg.edit_text(text, reply_markup=kb)
    else: await msg.answer(text, reply_markup=kb)

# ========== СТАТИСТИКА ==========

@router.message(F.text == "📊 Статистика")
@router.callback_query(F.data == "admin_stats")
async def admin_stats(event: Message | CallbackQuery):
    if isinstance(event, CallbackQuery):
        msg, is_cb = event.message, True
    else:
        if not is_admin(event.from_user.id): return
        msg, is_cb = event, False
    
    stats = get_statistics()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COALESCE(SUM(coins_balance), 0) FROM users")
    total_coins = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM referrals")
    total_refs = cursor.fetchone()[0]
    cursor.execute("SELECT COALESCE(SUM(total_amount), 0) FROM orders WHERE status='completed' AND date(created_at) >= date('now', '-7 days')")
    week_sales = cursor.fetchone()[0]
    cursor.execute("SELECT COALESCE(SUM(total_amount), 0) FROM orders WHERE status='completed' AND date(created_at) >= date('now', '-30 days')")
    month_sales = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM users WHERE date(registration_date) >= date('now', '-7 days')")
    new_users = cursor.fetchone()[0]
    conn.close()
    
    text = (
        f"📊 *Статистика*\n\n"
        f"👥 Пользователей: {stats['total_users']} (+{new_users} за неделю)\n"
        f"📦 Заказов: {stats['total_orders']}\n"
        f"📅 Сегодня: {stats['today_orders']}\n"
        f"💰 Продажи всего: {stats['total_sales']}💵\n"
        f"📆 За неделю: {week_sales}💵\n"
        f"📅 За месяц: {month_sales}💵\n"
        f"🍀 Монет у всех: {total_coins} 🪙\n"
        f"👥 Рефералов: {total_refs}\n"
    )
    
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Меню", callback_data="admin_menu")]])
    if is_cb: await msg.edit_text(text, reply_markup=kb)
    else: await msg.answer(text, reply_markup=kb)

# ========== РАССЫЛКА ==========

@router.message(F.text == "📢 Рассылка")
@router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast(event: Message | CallbackQuery, state: FSMContext):
    if isinstance(event, CallbackQuery):
        msg = event.message
    else:
        if not is_admin(event.from_user.id): return
        msg = event
    
    await msg.answer("📢 *Рассылка*\n\nОтправьте текст, фото, видео или GIF для рассылки всем пользователям.\n\nДля отмены: /cancel", parse_mode="Markdown")
    await state.set_state(AdminStates.waiting_for_broadcast)

@router.message(AdminStates.waiting_for_broadcast)
async def process_broadcast(message: Message, state: FSMContext):
    if message.text == "/cancel":
        await state.clear()
        await message.answer("❌ Рассылка отменена")
        return
    
    users = get_all_users()
    sent, errors = 0, 0
    
    for user in users:
        try:
            if message.photo:
                await message.bot.send_photo(user['user_id'], message.photo[-1].file_id, caption=message.caption or "")
            elif message.video:
                await message.bot.send_video(user['user_id'], message.video.file_id, caption=message.caption or "")
            elif message.animation:
                await message.bot.send_animation(user['user_id'], message.animation.file_id, caption=message.caption or "")
            elif message.document:
                await message.bot.send_document(user['user_id'], message.document.file_id, caption=message.caption or "")
            else:
                await message.bot.send_message(user['user_id'], message.text or "")
            sent += 1
        except:
            errors += 1
    
    add_log("broadcast", message.from_user.id, f"Отправлено: {sent}, Ошибок: {errors}")
    
    await state.clear()

# ========== НОВОСТИ ==========

@router.message(F.text == "📰 Новости")
@router.callback_query(F.data == "admin_news")
async def admin_news(event: Message | CallbackQuery):
    if isinstance(event, CallbackQuery):
        msg = event.message
    else:
        if not is_admin(event.from_user.id): return
        msg = event
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM news ORDER BY is_pinned DESC, created_at DESC LIMIT 10")
    news = cursor.fetchall()
    conn.close()
    
    text = "📰 *Новости*\n\n"
    if news:
        for n in news:
            pin = "📌 " if n['is_pinned'] else ""
            text += f"{pin}*{n['title']}*\n{n['content'][:100]}...\n\n"
    else:
        text += "Новостей нет\n\n"
    
    text += "📝 /add_news — добавить\n🗑 /delete_news_ID — удалить\n📌 /pin_news_ID — закрепить"
    
    await msg.answer(text)

@router.message(F.text.startswith("/add_news"))
async def add_news_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id): return
    await message.answer("📰 Новая новость\n\nОтправьте заголовок:")
    await state.set_state(AdminStates.waiting_for_news_title)

@router.message(AdminStates.waiting_for_news_title)
async def news_title(message: Message, state: FSMContext):
    await state.update_data(news_title=message.text)
    await message.answer("Отправьте текст новости:")
    await state.set_state(AdminStates.waiting_for_news_content)

@router.message(AdminStates.waiting_for_news_content)
async def news_content(message: Message, state: FSMContext):
    await state.update_data(news_content=message.text)
    await message.answer("Отправьте фото (или /skip):")
    await state.set_state(AdminStates.waiting_for_news_media)

@router.message(AdminStates.waiting_for_news_media)
async def news_media(message: Message, state: FSMContext):
    data = await state.get_data()
    image_id = message.photo[-1].file_id if message.photo else None
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO news (title, content, image_id) VALUES (?, ?, ?)",
                   (data['news_title'], data['news_content'], image_id))
    conn.commit()
    conn.close()
    
    add_log("news_add", message.from_user.id, f"Новость: {data['news_title']}")
    await message.answer("✅ Новость добавлена!")
    await state.clear()

# ========== НОВЫЙ ВАЙП ==========

@router.message(F.text == "🌸 Новый вайп")
@router.callback_query(F.data == "admin_wipe")
async def admin_wipe(event: Message | CallbackQuery):
    if isinstance(event, CallbackQuery):
        msg = event.message
    else:
        if not is_admin(event.from_user.id): return
        msg = event
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚠️ ДА, СДЕЛАТЬ ВАЙП", callback_data="admin_wipe_confirm")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_menu")]
    ])
    
    text = (
        "🌸 *Новый вайп*\n\n"
        "⚠️ *Необратимое действие!*\n\n"
        "Будет выполнено:\n"
        "• Закрыт магазин\n"
        "• Обнулены все Монеты\n"
        "• Сброшены реферальные бонусы\n"
        "• Закрыты промокоды\n\n"
        "*Подтвердите:*"
    )
    
    if isinstance(event, CallbackQuery):
        await msg.edit_text(text, reply_markup=kb)
    else:
        await msg.answer(text, reply_markup=kb)

@router.callback_query(F.data == "admin_wipe_confirm")
async def admin_wipe_confirm(callback: CallbackQuery):
    reset_all_coins()
    reset_referrals()
    set_setting("shop_open", False)
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE promocodes SET is_active = 0")
    conn.commit()
    conn.close()
    
    add_log("wipe", callback.from_user.id, "Выполнен новый вайп")
    
    await callback.message.edit_text(
        "✅ *Новый вайп выполнен!*\n\nМагазин закрыт.\nВсе Монеты обнулены.\nПромокоды деактивированы.",
        parse_mode="Markdown"
    )



# ========== НАСТРОЙКИ ==========

@router.message(F.text == "⚙ Настройки")
@router.callback_query(F.data == "admin_settings")
async def admin_settings(event: Message | CallbackQuery):
    if isinstance(event, CallbackQuery):
        msg = event.message
        is_cb = True
    else:
        if not is_admin(event.from_user.id): return
        msg = event
        is_cb = False
    
    settings = {
        "shop_name": get_setting("shop_name", "SAKURA STORE"),
        "shop_open": get_setting("shop_open", True),
        "stars_rate": get_setting("stars_rate", 40),
        "reviews_chat": get_setting("reviews_chat", ""),
        "telegram_channel": get_setting("telegram_channel", ""),
        "manager_username": get_setting("manager_username", "@Mik55554"),
        "mortal_nickname": get_setting("mortal_nickname", "MortalKhan95290"),
        "servers": get_setting("servers", ["Сервер 1", "Сервер 2", "Сервер 3", "Сервер 4"]),
        "about_text": get_setting("about_text", ""),
        "rules_text": get_setting("rules_text", ""),
        "discount_3plus_percent": get_setting("discount_3plus_percent", 5),
        "coins_rate": get_setting("coins_rate", 10),
        "referral_percent": get_setting("referral_percent", 2),
    }
    
    servers_str = ", ".join(settings['servers']) if settings['servers'] else "Не заданы"
    
    text = (
        f"⚙ *Настройки магазина*\n\n"
        f"1. Название: {settings['shop_name']}\n"
        f"2. Магазин: {'🟢 Открыт' if settings['shop_open'] else '🔴 Закрыт'}\n"
        f"3. Курс Stars: 1⭐ = {settings['stars_rate']}💵\n"
        f"4. Чат отзывов: {settings['reviews_chat'] or 'Не задан'}\n"
        f"5. Telegram-канал: {settings['telegram_channel'] or 'Не задан'}\n"
        f"6. Менеджер: {settings['manager_username']}\n"
        f"7. Ник Mortal: {settings['mortal_nickname']}\n"
        f"8. Серверы: {servers_str}\n"
        f"9. Скидка 3+: {settings['discount_3plus_percent']}%\n"
        f"10. Кэшбэк: {settings['coins_rate']}%\n"
        f"11. Реферал: {settings['referral_percent']}%\n\n"
        f"Для изменения нажмите на кнопку ниже:"
    )
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🟢 Открыть/Закрыть", callback_data="admin_toggle_shop")],
        [InlineKeyboardButton(text="✏️ Изменить настройку", callback_data="admin_edit_setting")],
        [InlineKeyboardButton(text="🔙 Меню", callback_data="admin_menu")]
    ])
    
    if is_cb:
        await msg.edit_text(text, reply_markup=kb)
    else:
        await msg.answer(text, reply_markup=kb)

@router.callback_query(F.data == "admin_toggle_shop")
async def admin_toggle_shop(callback: CallbackQuery):
    current = get_setting("shop_open", True)
    set_setting("shop_open", not current)
    add_log("settings", callback.from_user.id, f"Магазин {'закрыт' if current else 'открыт'}")
    await callback.answer(f"Магазин {'закрыт' if current else 'открыт'}")
    await admin_settings(callback)

@router.callback_query(F.data == "admin_edit_setting")
async def admin_edit_setting_menu(callback: CallbackQuery):
    """Меню выбора настройки для изменения"""
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1. Название", callback_data="set_shop_name")],
        [InlineKeyboardButton(text="3. Курс Stars", callback_data="set_stars_rate")],
        [InlineKeyboardButton(text="4. Чат отзывов", callback_data="set_reviews_chat")],
        [InlineKeyboardButton(text="5. Telegram-канал", callback_data="set_telegram_channel")],
        [InlineKeyboardButton(text="6. Менеджер", callback_data="set_manager_username")],
        [InlineKeyboardButton(text="7. Ник Mortal", callback_data="set_mortal_nickname")],
        [InlineKeyboardButton(text="8. Серверы", callback_data="set_servers")],
        [InlineKeyboardButton(text="9. Скидка 3+", callback_data="set_discount")],
        [InlineKeyboardButton(text="10. Кэшбэк %", callback_data="set_coins_rate")],
        [InlineKeyboardButton(text="11. Реферал %", callback_data="set_referral_percent")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_settings")]
    ])
    
    await callback.message.edit_text("✏️ *Выберите настройку для изменения:*", reply_markup=kb)

@router.callback_query(F.data.startswith("set_"))
async def admin_set_setting(callback: CallbackQuery, state: FSMContext):
    """Запрос нового значения настройки"""
    setting_key = callback.data.replace("set_", "")
    
    setting_names = {
        "shop_name": "Название магазина",
        "stars_rate": "Курс Stars (1⭐ = X💵)",
        "reviews_chat": "Ссылка на чат отзывов",
        "telegram_channel": "Ссылка на Telegram-канал",
        "manager_username": "Username менеджера",
        "mortal_nickname": "Ник MortalKhan95290",
        "servers": "Список серверов (через запятую)",
        "discount": "Размер скидки 3+ (%)",
        "coins_rate": "Курс начисления Монет (%)",
        "referral_percent": "Реферальный процент (%)"
    }
    
    current = get_setting(setting_key, "")
    if setting_key in ["servers"] and isinstance(current, list):
        current = ", ".join(current)
    
    await state.update_data(setting_key=setting_key)
    await callback.message.edit_text(
        f"✏️ *{setting_names.get(setting_key, setting_key)}*\n\n"
        f"Текущее значение: {current}\n\n"
        f"Отправьте новое значение:"
    )
    await state.set_state(AdminStates.waiting_for_setting_value)
    await callback.answer()

@router.message(AdminStates.waiting_for_setting_value)
async def process_setting_value(message: Message, state: FSMContext):
    """Сохранение нового значения настройки"""
    data = await state.get_data()
    setting_key = data['setting_key']
    value = message.text.strip()
    
    # Обработка специальных типов
    if setting_key == "stars_rate":
        value = int(value)
    elif setting_key == "discount":
        value = int(value)
    elif setting_key == "coins_rate":
        value = int(value)
    elif setting_key == "referral_percent":
        value = int(value)
    elif setting_key == "servers":
        value = [s.strip() for s in value.split(",")]
    
    set_setting(setting_key, value)
    add_log("settings", message.from_user.id, f"Изменена настройка {setting_key}: {value}")
    
    await message.answer(f"✅ Настройка обновлена!")
    await state.clear()

# ========== ЛОГИ ==========

@router.message(F.text == "📝 Логи")
@router.callback_query(F.data == "admin_logs")
async def admin_logs(event: Message | CallbackQuery):
    if isinstance(event, CallbackQuery):
        msg = event.message
    else:
        if not is_admin(event.from_user.id): return
        msg = event
    
    logs = get_logs(30)
    text = "📝 *Логи*\n\n"
    for log in logs:
        text += f"[{log['created_at'][:19]}] {log['action']} | ID:{log['admin_id']}\n"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Меню", callback_data="admin_menu")]])
    if isinstance(event, CallbackQuery):
        await msg.edit_text(text, reply_markup=kb)
    else:
        await msg.answer(text, reply_markup=kb)

# ========== БЭКАП ==========

@router.message(F.text == "💾 Бэкап")
@router.callback_query(F.data == "admin_backup")
async def admin_backup(event: Message | CallbackQuery):
    if isinstance(event, CallbackQuery):
        msg = event.message
        user_id = event.from_user.id
        is_cb = True
    else:
        if not is_admin(event.from_user.id): return
        msg = event
        user_id = event.from_user.id
        is_cb = False
    
    os.makedirs("backups", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"backups/sakura_backup_{timestamp}.db"
    shutil.copy2("database/sakura_bot.db", backup_path)
    
    add_log("backup", user_id, backup_path)
    
    # Отправляем файл в чат
    from aiogram.types import FSInputFile
    backup_file = FSInputFile(backup_path)
    
    await msg.answer_document(
        document=backup_file,
        caption=f"💾 Бэкап создан!\n📅 {timestamp}\n📁 sakura_backup_{timestamp}.db"
    )
    
    if is_cb:
        await event.answer("✅ Бэкап отправлен")  # Исправлено: event.answer вместо callback.answer

# ========== ОБРАБОТЧИК ДЛЯ ПОЛЬЗОВАТЕЛЕЙ ==========

@router.message(F.text == "📰 Новости")
async def show_news_user(message: Message):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM news WHERE is_active = 1 ORDER BY is_pinned DESC, created_at DESC LIMIT 10")
    news = cursor.fetchall()
    conn.close()
    
    if not news:
        await message.answer("📰 Новостей пока нет")
        return
    
    for n in news:
        text = f"{'📌 ' if n['is_pinned'] else ''}*{n['title']}*\n\n{n['content']}"
        if n['image_id']:
            await message.answer_photo(n['image_id'], caption=text)
        else:
            await message.answer(text)

# В конец admin_full.py добавить:

@router.message(F.text.startswith("/add_manager"))
async def add_manager_cmd(message: Message):
    from database.admin_db import add_manager
    from config import ADMIN_IDS
    
    if message.from_user.id not in ADMIN_IDS:
        return
    
    try:
        parts = message.text.split()
        user_id = int(parts[1])
        if add_manager(user_id):
            await message.answer(f"✅ Менеджер добавлен: {user_id}")
        else:
            await message.answer("❌ Уже менеджер")
    except:
        await message.answer("❌ /add_manager ID")

@router.message(F.text.startswith("/add_moder"))
async def add_moder_cmd(message: Message):
    from database.admin_db import add_moder
    from config import ADMIN_IDS
    
    if message.from_user.id not in ADMIN_IDS:
        return
    
    try:
        parts = message.text.split()
        user_id = int(parts[1])
        if add_moder(user_id):
            await message.answer(f"✅ Модератор добавлен: {user_id}")
        else:
            await message.answer("❌ Уже модератор")
    except:
        await message.answer("❌ /add_moder ID")

@router.message(F.text.startswith("/remove_manager"))
async def remove_manager_cmd(message: Message):
    """Разжалует менеджера"""
    from config import ADMIN_IDS, MANAGER_IDS
    
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ Только владелец может управлять персоналом")
        return
    
    try:
        parts = message.text.split()
        user_id = int(parts[1])
        
        if user_id in MANAGER_IDS:
            MANAGER_IDS.remove(user_id)
            add_log("remove_manager", message.from_user.id, f"Менеджер удалён: {user_id}")
            await message.answer(f"✅ Пользователь {user_id} разжалован.\nПопросите его перезапустить бота: /start")
            try:
                await message.bot.send_message(user_id, "🔔 Вы сняты с должности менеджера.\nПерезапустите бота: /start")
            except: pass
        else:
            await message.answer("❌ Не является менеджером")
    except:
        await message.answer("❌ /remove_manager ID")

@router.message(F.text.startswith("/remove_moder"))
async def remove_moder_cmd(message: Message):
    """Разжалует модератора"""
    from config import ADMIN_IDS, MODER_IDS
    
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ Только владелец может управлять персоналом")
        return
    
    try:
        parts = message.text.split()
        user_id = int(parts[1])
        
        if user_id in MODER_IDS:
            MODER_IDS.remove(user_id)
            add_log("remove_moder", message.from_user.id, f"Модератор удалён: {user_id}")
            await message.answer(f"✅ Пользователь {user_id} разжалован.\nПопросите его перезапустить бота: /start")
            try:
                await message.bot.send_message(user_id, "🔔 Вы сняты с должности модератора.\nПерезапустите бота: /start")
            except: pass
        else:
            await message.answer("❌ Не является модератором")
    except:
        await message.answer("❌ /remove_moder ID")

@router.message(F.text == "/staff")
async def staff_list(message: Message):
    """Показывает список персонала"""
    from config import ADMIN_IDS, MANAGER_IDS, MODER_IDS
    
    if message.from_user.id not in ADMIN_IDS:
        return
    
    text = "👥 Персонал SAKURA STORE\n\n"
    
    text += "👑 Владельцы:\n"
    for uid in ADMIN_IDS:
        user = get_user_by_id(uid)
        name = user['first_name'] or f"ID:{uid}" if user else f"ID:{uid}"
        text += f"  • {name} (`{uid}`)\n"
    
    text += "\n🔧 Менеджеры:\n"
    if MANAGER_IDS:
        for uid in MANAGER_IDS:
            user = get_user_by_id(uid)
            name = user['first_name'] or f"ID:{uid}" if user else f"ID:{uid}"
            text += f"  • {name} (`{uid}`)\n"
    else:
        text += "  Нет\n"
    
    text += "\n🛡 Модераторы:\n"
    if MODER_IDS:
        for uid in MODER_IDS:
            user = get_user_by_id(uid)
            name = user['first_name'] or f"ID:{uid}" if user else f"ID:{uid}"
            text += f"  • {name} (`{uid}`)\n"
    else:
        text += "  Нет\n"
    
    await message.answer(text)

@router.message(F.text.startswith("/add_promo"))
async def add_promo_start(message: Message, state: FSMContext):
    """Начало создания промокода"""
    if not is_admin(message.from_user.id): 
        return
    
    await message.answer(
        "🎟 *Создание промокода*\n\n"
        "Отправьте *код* промокода (например: SALE20):",
        parse_mode="Markdown"
    )
    await state.set_state(AdminStates.waiting_for_promocode_code)

@router.message(AdminStates.waiting_for_promocode_code)
async def promo_code(message: Message, state: FSMContext):
    """Получает код"""
    code = message.text.strip().upper()
    
    # Проверяем уникальность
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM promocodes WHERE code = ?", (code,))
    if cursor.fetchone():
        conn.close()
        await message.answer("❌ Такой промокод уже существует!")
        return
    conn.close()
    
    await state.update_data(promo_code=code)
    
    # Предлагаем выбрать тип
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Процент (%)", callback_data="promo_type_percent")],
        [InlineKeyboardButton(text="💰 Фиксированная сумма", callback_data="promo_type_fixed")]
    ])
    await message.answer(f"Код: `{code}`\n\nВыберите *тип скидки*:", reply_markup=kb, parse_mode="Markdown")

@router.callback_query(F.data.startswith("promo_type_"))
async def promo_type(callback: CallbackQuery, state: FSMContext):
    """Выбор типа скидки"""
    promo_type = callback.data.replace("promo_type_", "")
    await state.update_data(promo_type=promo_type)
    
    type_name = "процент скидки (например: 10)" if promo_type == "percent" else "сумму скидки в 💵 (например: 1000)"
    await callback.message.edit_text(
        f"Тип: {'Процент' if promo_type == 'percent' else 'Фиксированная сумма'}\n\n"
        f"Отправьте {type_name}:"
    )
    await state.set_state(AdminStates.waiting_for_promocode_discount)
    await callback.answer()

@router.message(AdminStates.waiting_for_promocode_discount)
async def promo_discount(message: Message, state: FSMContext):
    """Получает размер скидки"""
    try:
        discount = int(message.text)
        if discount < 1:
            await message.answer("❌ Скидка должна быть больше 0")
            return
        
        data = await state.get_data()
        if data['promo_type'] == 'percent' and discount > 100:
            await message.answer("❌ Процент не может быть больше 100")
            return
        
        await state.update_data(promo_discount=discount)
        
        # Выбор категории
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🛍 Все товары", callback_data="promo_cat_all")],
            [InlineKeyboardButton(text="🛡 Привилегии", callback_data="promo_cat_privileges")],
            [InlineKeyboardButton(text="❤️ Рубины", callback_data="promo_cat_rubins")],
            [InlineKeyboardButton(text="🧸 Питомцы", callback_data="promo_cat_pets")],
            [InlineKeyboardButton(text="🎁 Паки", callback_data="promo_cat_packs")],
        ])
        await message.answer("Выберите *категорию товаров* для промокода:", reply_markup=kb, parse_mode="Markdown")
        await state.set_state(AdminStates.waiting_for_promocode_category)
    except:
        await message.answer("❌ Отправьте число")

@router.callback_query(F.data.startswith("promo_cat_"))
async def promo_category(callback: CallbackQuery, state: FSMContext):
    """Выбор категории"""
    category = callback.data.replace("promo_cat_", "")
    cat_names = {
        "all": "Все товары",
        "privileges": "🛡 Привилегии",
        "rubins": "❤️ Рубины",
        "pets": "🧸 Питомцы",
        "packs": "🎁 Паки"
    }
    await state.update_data(promo_category=category)
    
    await callback.message.edit_text(
        f"Категория: {cat_names.get(category, category)}\n\n"
        f"Отправьте *максимальное количество использований* (0 = без ограничений):",
        parse_mode="Markdown"
    )
    await state.set_state(AdminStates.waiting_for_promocode_max_uses)
    await callback.answer()

@router.message(AdminStates.waiting_for_promocode_max_uses)
async def promo_max_uses(message: Message, state: FSMContext):
    """Получает макс. использований"""
    try:
        max_uses = int(message.text)
        if max_uses < 0:
            await message.answer("❌ Не может быть отрицательным")
            return
        
        await state.update_data(promo_max_uses=max_uses if max_uses > 0 else None)
        await message.answer(
            f"Макс. использований: {max_uses or 'Без ограничений'}\n\n"
            f"Отправьте *минимальную сумму заказа* (0 = без ограничений):",
            parse_mode="Markdown"
        )
        await state.set_state(AdminStates.waiting_for_promocode_min_amount)
    except:
        await message.answer("❌ Отправьте число")

@router.message(AdminStates.waiting_for_promocode_min_amount)
async def promo_min_amount(message: Message, state: FSMContext):
    """Получает мин. сумму"""
    try:
        min_amount = int(message.text)
        if min_amount < 0:
            await message.answer("❌ Не может быть отрицательным")
            return
        
        await state.update_data(promo_min_amount=min_amount)
        await message.answer(
            f"Мин. сумма: {min_amount}💵\n\n"
            f"Отправьте *дату окончания* в формате ДД.ММ.ГГГГ\n"
            f"(или 0 = без ограничений):",
            parse_mode="Markdown"
        )
        await state.set_state(AdminStates.waiting_for_promocode_valid_until)
    except:
        await message.answer("❌ Отправьте число")

@router.message(AdminStates.waiting_for_promocode_valid_until)
async def promo_valid_until(message: Message, state: FSMContext):
    """Сохраняет промокод"""
    data = await state.get_data()
    
    valid_until = None
    if message.text.strip() != "0":
        try:
            from datetime import datetime
            valid_date = datetime.strptime(message.text.strip(), "%d.%m.%Y")
            valid_until = valid_date.strftime("%Y-%m-%d 23:59:59")
        except:
            await message.answer("❌ Неверный формат даты. Используйте ДД.ММ.ГГГГ или 0")
            return
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO promocodes (code, discount_percent, category, max_uses, min_amount, valid_until)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data['promo_code'],
            data['promo_discount'],
            data['promo_category'],
            data['promo_max_uses'],
            data['promo_min_amount'],
            valid_until
        ))
        
        conn.commit()
        
        add_log("promo_add", message.from_user.id,
                f"Промокод {data['promo_code']}: -{data['promo_discount']}{'%' if data['promo_type'] == 'percent' else '💵'}")
        
        cat_names = {"all": "Все", "privileges": "Привилегии", "rubins": "Рубины", "pets": "Питомцы", "packs": "Паки"}
        
        await message.answer(
            f"✅ *Промокод создан!*\n\n"
            f"🔑 Код: `{data['promo_code']}`\n"
            f"📊 Тип: {'% скидка' if data['promo_type'] == 'percent' else '💵 скидка'}\n"
            f"🎁 Скидка: {data['promo_discount']}{'%' if data['promo_type'] == 'percent' else '💵'}\n"
            f"📂 Категория: {cat_names.get(data['promo_category'], 'Все')}\n"
            f"👥 Макс. использований: {data['promo_max_uses'] or 'Без ограничений'}\n"
            f"💰 Мин. сумма: {data['promo_min_amount']}💵\n"
            f"📅 Действует до: {message.text if message.text != '0' else 'Без ограничений'}",
            parse_mode="Markdown"
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
    finally:
        conn.close()
    
    await state.clear()

@router.message(F.text.startswith("/delete_promo"))
async def delete_promo(message: Message):
    """Удаляет промокод"""
    if not is_admin(message.from_user.id): 
        return
    
    try:
        code = message.text.replace("/delete_promo ", "").strip().upper()
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM promocodes WHERE code = ?", (code,))
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        if deleted:
            add_log("promo_delete", message.from_user.id, f"Промокод {code} удалён")
            await message.answer(f"✅ Промокод {code} удалён")
        else:
            await message.answer(f"❌ Промокод {code} не найден")
    except:
        await message.answer("❌ Используйте: /delete_promo КОД")

@router.message(F.text.startswith("/edit_promo"))
async def edit_promo_cmd(message: Message):
    """Изменить скидку промокода: /edit_promo КОД НОВАЯ_СКИДКА"""
    if not is_admin(message.from_user.id): 
        return
    
    try:
        parts = message.text.split()
        if len(parts) < 3:
            await message.answer("❌ Используйте: /edit_promo КОД НОВАЯ_СКИДКА\nПример: /edit_promo SALE20 15")
            return
        
        code = parts[1].upper()
        new_discount = int(parts[2])
        
        if new_discount < 1 or new_discount > 100:
            await message.answer("❌ Скидка должна быть от 1 до 100%")
            return
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE promocodes SET discount_percent = ? WHERE code = ?", (new_discount, code))
        
        if cursor.rowcount == 0:
            conn.close()
            await message.answer(f"❌ Промокод {code} не найден")
            return
        
        conn.commit()
        conn.close()
        
        add_log("promo_edit", message.from_user.id, f"Промокод {code}: скидка изменена на {new_discount}%")
        await message.answer(f"✅ Промокод {code} изменён: скидка {new_discount}%")
    except ValueError:
        await message.answer("❌ Скидка должна быть числом")
    except:
        await message.answer("❌ Ошибка")

@router.message(F.text.startswith("/off_promo"))
async def off_promo_cmd(message: Message):
    """Отключить промокод: /off_promo КОД"""
    if not is_admin(message.from_user.id): 
        return
    
    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.answer("❌ Используйте: /off_promo КОД\nПример: /off_promo SALE20")
            return
        
        code = parts[1].upper()
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE promocodes SET is_active = 0 WHERE code = ?", (code,))
        
        if cursor.rowcount == 0:
            conn.close()
            await message.answer(f"❌ Промокод {code} не найден")
            return
        
        conn.commit()
        conn.close()
        
        add_log("promo_off", message.from_user.id, f"Промокод {code} отключен")
        await message.answer(f"🔴 Промокод {code} отключен")
    except:
        await message.answer("❌ Ошибка")

@router.message(F.text.startswith("/on_promo"))
async def on_promo_cmd(message: Message):
    """Включить промокод: /on_promo КОД"""
    if not is_admin(message.from_user.id): 
        return
    
    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.answer("❌ Используйте: /on_promo КОД\nПример: /on_promo SALE20")
            return
        
        code = parts[1].upper()
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE promocodes SET is_active = 1 WHERE code = ?", (code,))
        
        if cursor.rowcount == 0:
            conn.close()
            await message.answer(f"❌ Промокод {code} не найден")
            return
        
        conn.commit()
        conn.close()
        
        add_log("promo_on", message.from_user.id, f"Промокод {code} включен")
        await message.answer(f"🟢 Промокод {code} включен")
    except:
        await message.answer("❌ Ошибка")