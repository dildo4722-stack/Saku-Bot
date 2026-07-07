# handlers/shop.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from typing import Dict, List

from keyboards.main_menu import get_main_menu_keyboard
from keyboards.shop_keyboards import (
    get_shop_categories_keyboard,
    get_back_to_shop_keyboard,
    get_product_actions_keyboard,
    get_cart_keyboard,
    get_payment_methods_keyboard,
    get_servers_keyboard,
    get_confirm_order_keyboard,
    get_payment_instructions_keyboard,
    get_contact_manager_keyboard,
    get_promocode_skip_keyboard
)
from data.products import get_product_by_id, get_products_by_category, get_category_info
from database.users_db import add_coins, update_user, get_user, get_user_status
from database.orders_db import create_order, add_order_item
from database.referrals_db import get_referrer, calculate_referral_bonus, add_referral_bonus
from database.promocodes_db import check_promocode, use_promocode
from handlers.cashback import calculate_cashback

router = Router()

user_carts: Dict[int, List[dict]] = {}

class OrderStates(StatesGroup):
    waiting_for_promocode = State()
    waiting_for_nickname = State()
    waiting_for_screenshot = State()

def calculate_total_with_discounts(cart: list, promocode_data: dict = None) -> dict:
    """Рассчитывает итоговую сумму со всеми скидками"""
    total = sum(item["price"] * item["quantity"] for item in cart)
    items_count = sum(item["quantity"] for item in cart)
    
    discount_3plus = 0
    if items_count >= 3:
        discount_3plus = int(total * 0.05)
    
    promocode_discount = 0
    promocode_percent = 0
    if promocode_data:
        promocode_percent = promocode_data.get('discount_percent', 0)
        promocode_discount = int(total * (promocode_percent / 100))
    
    total_discount = discount_3plus + promocode_discount
    total_with_discount = int(total - total_discount)
    
    return {
        'total': total,
        'items_count': items_count,
        'discount_3plus': discount_3plus,
        'promocode_discount': promocode_discount,
        'promocode_percent': promocode_percent,
        'total_discount': total_discount,
        'total_with_discount': total_with_discount
    }

def format_cart_message(user_id: int, promocode_data: dict = None) -> str:
    """Форматирует сообщение с содержимым корзины"""
    cart = user_carts.get(user_id, [])
    if not cart:
        return "🛒 Ваша корзина пуста"
    
    calc = calculate_total_with_discounts(cart, promocode_data)
    
    message = "🛒 *Ваша корзина*\n\n"
    
    for i, item in enumerate(cart, 1):
        message += f"{i}. {item['name']} x{item['quantity']} = {item['price'] * item['quantity']}💵\n"
    
    message += f"\n📦 Всего товаров: {calc['items_count']}"
    message += f"\n💰 Общая стоимость: {calc['total']}💵"
    
    if calc['discount_3plus'] > 0:
        message += f"\n🎁 Скидка (5% за 3+ товара): -{calc['discount_3plus']}💵"
    
    if calc['promocode_discount'] > 0:
        message += f"\n🎟 Скидка по промокоду ({calc['promocode_percent']}%): -{calc['promocode_discount']}💵"
    
    coins = int(calc['total_with_discount'] * 0.1)
    
    message += f"\n🪙 Начисление монет: {coins}"
    message += f"\n💎 Итого к оплате: {calc['total_with_discount']}💵"
    
    return message

async def show_final_price(message: Message, state: FSMContext, is_callback: bool = False):
    """Показывает итоговую стоимость после применения промокода"""
    user_id = message.chat.id if is_callback else message.from_user.id
    cart = user_carts.get(user_id, [])
    
    data = await state.get_data()
    payment_method = data.get('payment_method', 'game_currency')
    
    promocode_data = None
    if data.get('promocode'):
        promocode_data = {'discount_percent': data.get('discount_percent', 0)}
    
    calc = calculate_total_with_discounts(cart, promocode_data)
    
    from database.admin_settings import get_setting
    
    payment_name = "💵 Игровая валюта" if payment_method == "game_currency" else "⭐ Telegram Stars"
    mortal_nick = get_setting("mortal_nickname", "MortalKhan95290")
    
    price_text = (
        f"💳 *Итоговая стоимость*\n\n"
        f"🛒 Товаров: {calc['items_count']} шт.\n"
        f"💰 Сумма: {calc['total']}💵\n"
    )
    
    if calc['discount_3plus'] > 0:
        price_text += f"🎁 Скидка (5%): -{calc['discount_3plus']}💵\n"
    
    if calc['promocode_discount'] > 0:
        price_text += f"🎟 Промокод ({calc['promocode_percent']}%): -{calc['promocode_discount']}💵\n"
    
    price_text += f"\n💎 *Итого: {calc['total_with_discount']}💵*\n"
    price_text += f"💳 Способ оплаты: {payment_name}\n\n"
    
    if payment_method == "game_currency":
        price_text += f"🌍 Выберите сервер для выдачи:\n"
        keyboard = get_servers_keyboard()
    else:
        price_text += "⭐ Оплата через Telegram Stars производится через менеджера."
        keyboard = get_contact_manager_keyboard()
    
    if is_callback:
        await message.edit_text(price_text, reply_markup=keyboard, parse_mode="Markdown")
    else:
        await message.answer(price_text, reply_markup=keyboard, parse_mode="Markdown")
    
    await state.set_state(OrderStates.waiting_for_nickname)

# === МАГАЗИН ===

@router.callback_query(F.data == "shop")
@router.message(F.text == "🛍 Магазин")
async def show_shop(message: Message | CallbackQuery):
    """Показывает категории магазина"""
    if isinstance(message, CallbackQuery):
        await message.message.edit_text(
            "🛍 *Магазин SAKURA STORE*\n\nВыберите категорию товаров:",
            reply_markup=get_shop_categories_keyboard(),
            parse_mode="Markdown"
        )
    else:
        await message.answer(
            "🛍 *Магазин SAKURA STORE*\n\nВыберите категорию товаров:",
            reply_markup=get_shop_categories_keyboard(),
            parse_mode="Markdown"
        )

@router.callback_query(F.data.startswith("category_"))
async def show_category_products(callback: CallbackQuery):
    """Показывает товары выбранной категории"""
    category = callback.data.replace("category_", "")
    products = get_products_by_category(category)
    
    if not products:
        await callback.answer("В этой категории пока нет товаров")
        return
    
    category_names = {
        "privileges": "🛡 Привилегии",
        "rubins": "❤️ Рубины",
        "pets": "🧸 Питомцы",
        "packs": "🎁 Подарочные паки",
        "certificates": "🎟 Подарочные сертификаты"
    }
    
    message_text = f"*{category_names.get(category, 'Товары')}*\n\n"
    
    for product in products:
        if product["price_game"] is not None:
            price_text = f"💵 {product['price_game']:,}💵".replace(",", " ")
            stars_text = f"⭐ {product['price_stars']}⭐"
            message_text += f"• {product['name']}\n  {price_text} | {stars_text}\n\n"
        else:
            message_text += f"• {product['name']}\n  {product['description']}\n\n"
    
    additional_info = get_category_info(category)
    if additional_info:
        message_text += additional_info
    
    buttons = []
    for product in products:
        if product["price_game"] is not None:
            button_text = f"{product['name']} - {product['price_game']:,}💵".replace(",", " ")
        else:
            button_text = f"{product['name']} - Предзаказ"
        
        buttons.append([InlineKeyboardButton(text=button_text, callback_data=f"product_{product['id']}")])
    
    buttons.append([InlineKeyboardButton(text="🔙 Назад к категориям", callback_data="shop")])
    buttons.append([InlineKeyboardButton(text="🛒 Корзина", callback_data="cart")])
    buttons.append([InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")])
    
    await callback.message.edit_text(message_text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode="Markdown")

@router.callback_query(F.data.startswith("product_"))
async def show_product(callback: CallbackQuery):
    """Показывает информацию о товаре"""
    product_id = int(callback.data.replace("product_", ""))
    product = get_product_by_id(product_id)
    
    if not product:
        await callback.answer("Товар не найден")
        return
    
    is_preorder = product["price_game"] is None
    
    if not is_preorder:
        message_text = (
            f"*{product['name']}*\n\n"
            f"📝 {product['description']}\n"
            f"💰 Стоимость:\n"
            f"💵 Игровая валюта: {product['price_game']:,}💵\n"
            f"⭐ Stars: {product['price_stars']}⭐\n\n"
            f"Выберите действие:"
        ).replace(",", " ")
    else:
        message_text = (
            f"*{product['name']}*\n\n"
            f"🔥 {product['description']}\n\n"
            f"Для заказа свяжитесь с менеджером:\n"
            f"👤 @Mik55554"
        )
    
    current_text = callback.message.text or callback.message.caption
    if current_text == message_text:
        await callback.answer("Этот товар уже открыт")
        return
    
    await callback.message.edit_text(
        message_text,
        reply_markup=get_product_actions_keyboard(product_id, is_preorder),
        parse_mode="Markdown"
    )

@router.callback_query(F.data.startswith("add_to_cart_"))
async def add_to_cart(callback: CallbackQuery):
    """Добавляет товар в корзину"""
    product_id = int(callback.data.replace("add_to_cart_", ""))
    product = get_product_by_id(product_id)
    
    if not product:
        await callback.answer("Товар не найден")
        return
    
    if product["price_game"] is None:
        await callback.answer("Этот товар доступен только по предзаказу")
        return
    
    user_id = callback.from_user.id
    
    if user_id not in user_carts:
        user_carts[user_id] = []
    
    for item in user_carts[user_id]:
        if item["id"] == product_id:
            item["quantity"] += 1
            await callback.answer(f"{product['name']} добавлен в корзину (x{item['quantity']})")
            return
    
    user_carts[user_id].append({
        "id": product_id,
        "name": product["name"],
        "price": product["price_game"],
        "quantity": 1
    })
    
    await callback.answer(f"{product['name']} добавлен в корзину")

@router.callback_query(F.data == "cart")
@router.message(F.text == "🛒 Корзина")
async def show_cart(message: Message | CallbackQuery):
    """Показывает содержимое корзины"""
    user_id = message.from_user.id if isinstance(message, Message) else message.from_user.id
    cart_message = format_cart_message(user_id)
    
    if isinstance(message, CallbackQuery):
        await message.message.edit_text(cart_message, reply_markup=get_cart_keyboard(), parse_mode="Markdown")
    else:
        await message.answer(cart_message, reply_markup=get_cart_keyboard(), parse_mode="Markdown")

@router.callback_query(F.data == "clear_cart")
async def clear_cart(callback: CallbackQuery):
    """Очищает корзину"""
    user_carts[callback.from_user.id] = []
    await callback.answer("Корзина очищена")
    await show_cart(callback)

@router.callback_query(F.data == "checkout")
async def checkout(callback: CallbackQuery):
    """Оформление заказа - выбор способа оплаты"""
    if not user_carts.get(callback.from_user.id):
        await callback.answer("Ваша корзина пуста")
        return
    
    await callback.message.edit_text(
        "💳 *Выберите способ оплаты:*",
        reply_markup=get_payment_methods_keyboard(),
        parse_mode="Markdown"
    )

# === ОПЛАТА И ПРОМОКОД ===

@router.callback_query(F.data == "pay_game_currency")
async def pay_game_currency(callback: CallbackQuery, state: FSMContext):
    """Оплата игровой валютой - запрос промокода"""
    await state.update_data(payment_method="game_currency")
    
    await callback.message.edit_text(
        "🎟 *Введите промокод*\n\n"
        "Если у вас есть промокод, отправьте его сейчас.\n"
        "Если нет — нажмите кнопку «Пропустить».",
        reply_markup=get_promocode_skip_keyboard(),
        parse_mode="Markdown"
    )
    await state.set_state(OrderStates.waiting_for_promocode)

@router.callback_query(F.data == "pay_telegram_stars")
async def pay_telegram_stars(callback: CallbackQuery, state: FSMContext):
    """Оплата Telegram Stars - запрос промокода"""
    await state.update_data(payment_method="telegram_stars")
    
    await callback.message.edit_text(
        "🎟 *Введите промокод*\n\n"
        "Если у вас есть промокод, отправьте его сейчас.\n"
        "Если нет — нажмите кнопку «Пропустить».",
        reply_markup=get_promocode_skip_keyboard(),
        parse_mode="Markdown"
    )
    await state.set_state(OrderStates.waiting_for_promocode)

@router.message(OrderStates.waiting_for_promocode)
async def process_promocode(message: Message, state: FSMContext):
    """Обработка введенного промокода"""
    promocode = message.text.strip().upper()
    user_id = message.from_user.id
    cart = user_carts.get(user_id, [])
    
    if not cart:
        await message.answer("❌ Корзина пуста")
        await state.clear()
        return
    
    total = sum(item["price"] * item["quantity"] for item in cart)
    result = check_promocode(promocode, user_id, total)
    
    if not result["valid"]:
        await message.answer(f"{result['message']}\n\nПопробуйте другой код или нажмите «Пропустить».")
        return
    
    await state.update_data(
        promocode=promocode,
        promocode_id=result["promocode_id"],
        discount_percent=result["discount_percent"]
    )
    
    await message.answer(f"✅ Промокод *{promocode}* применен! Скидка {result['discount_percent']}%", parse_mode="Markdown")
    await show_final_price(message, state)

@router.callback_query(F.data == "skip_promocode")
async def skip_promocode(callback: CallbackQuery, state: FSMContext):
    """Пропуск ввода промокода"""
    await callback.answer()
    await show_final_price(callback.message, state, is_callback=True)

# === СЕРВЕР И НИК ===

@router.callback_query(F.data.startswith("server_"))
async def select_server(callback: CallbackQuery, state: FSMContext):
    """Выбор сервера и запрос ника"""
    server = callback.data.replace("server_", "")
    await state.update_data(server=f"Сервер {server}")
    
    await callback.message.edit_text("👤 Введите ваш игровой ник:")
    await state.set_state(OrderStates.waiting_for_nickname)

@router.message(OrderStates.waiting_for_nickname)
async def process_nickname(message: Message, state: FSMContext):
    """Обработка введенного ника"""
    nickname = message.text
    await state.update_data(nickname=nickname)
    
    data = await state.get_data()
    user_id = message.from_user.id
    cart = user_carts.get(user_id, [])
    
    calc = calculate_total_with_discounts(cart)
    
    # Убираем Markdown, используем обычный текст
    order_text = "⸻\n"
    order_text += "Ваш заказ\n\n"
    
    for item in cart:
        order_text += f"🛒 {item['name']} x{item['quantity']}\n"
    
    order_text += f"\nСтоимость: {calc['total_with_discount']}💵\n\n"
    order_text += f"Игровой ник: {nickname}\n\n"
    order_text += f"Сервер: {data['server']}\n\n"
    order_text += "⸻"
    
    # Отправляем БЕЗ parse_mode="Markdown"
    await message.answer(
        order_text,
        reply_markup=get_confirm_order_keyboard()
    )

# === ПОДТВЕРЖДЕНИЕ И ОПЛАТА ===

@router.callback_query(F.data == "confirm_order")
async def confirm_order(callback: CallbackQuery, state: FSMContext):
    """Подтверждение заказа и инструкция по оплате"""
    user_id = callback.from_user.id
    cart = user_carts.get(user_id, [])
    
    data = await state.get_data()
    payment_method = data.get('payment_method', 'game_currency')
    
    promocode_data = None
    if data.get('promocode'):
        promocode_data = {'discount_percent': data.get('discount_percent', 0)}
    
    calc = calculate_total_with_discounts(cart, promocode_data)
    
    if payment_method == "game_currency":
        # Получаем ник из настроек
        from database.admin_settings import get_setting
        mortal_nick = get_setting("mortal_nickname", "MortalKhan95290")
        
        instruction_text = (
            f"💳 *Инструкция по оплате*\n\n"
            f"Переведите *{calc['total_with_discount']}💵* игроку *{mortal_nick}*\n"
            f"на *Первом сервере MinePlanet*.\n\n"
            f"После оплаты нажмите кнопку ниже."
        )
        keyboard = get_payment_instructions_keyboard()
    else:
        instruction_text = (
            "⭐ *Оплата через Telegram Stars*\n\n"
            "Свяжитесь с менеджером для оплаты."
        )
        keyboard = get_contact_manager_keyboard()
    
    await callback.message.edit_text(instruction_text, reply_markup=keyboard, parse_mode="Markdown")

@router.callback_query(F.data == "i_paid")
async def i_paid(callback: CallbackQuery, state: FSMContext):
    """Запрос скриншота оплаты"""
    await callback.message.edit_text("📷 *Отправьте скриншот перевода*", parse_mode="Markdown")
    await state.set_state(OrderStates.waiting_for_screenshot)

@router.message(OrderStates.waiting_for_screenshot, F.photo)
async def process_screenshot(message: Message, state: FSMContext):
    """Обработка скриншота и создание заказа"""
    user_id = message.from_user.id
    cart = user_carts.get(user_id, [])
    
    # Сохраняем file_id скриншота
    screenshot_id = message.photo[-1].file_id
    
    user_data = get_user(user_id)
    if not user_data:
        await message.answer("❌ Ошибка: пользователь не найден")
        return
    
    data = await state.get_data()
    server = data.get('server', 'Не указан')
    nickname = data.get('nickname', 'Не указан')
    payment_method = data.get('payment_method', 'game_currency')
    
    promocode_data = None
    promocode = data.get('promocode')
    promocode_id = data.get('promocode_id')
    
    if promocode and promocode_id:
        promocode_data = {'discount_percent': data.get('discount_percent', 0)}
    
    calc = calculate_total_with_discounts(cart, promocode_data)
    
    status = get_user_status(user_data['total_purchases'] or 0)
    base_coins = calculate_cashback(calc['total_with_discount'])
    
    bonus_multiplier = 1.0
    if status['bonus_percent'] > 0:
        bonus_multiplier = 1.0 + (status['bonus_percent'] / 100.0)
    
    coins_earned = int(base_coins * bonus_multiplier)
    
    order_id = create_order(
        user_id=user_id,
        total_amount=calc['total_with_discount'],
        discount=calc['total_discount'],
        coins_earned=coins_earned,
        payment_method=payment_method,
        server=server,
        nickname=nickname,
        screenshot_id=screenshot_id
    )
    
    for item in cart:
        add_order_item(order_id=order_id, product_id=item['id'], product_name=item['name'], price=item['price'], quantity=item['quantity'])
    
    add_coins(user_id=user_id, amount=coins_earned, type="purchase", description=f"Кэшбэк за заказ #{order_id}", order_id=order_id)
    
    update_user(
        user_id=user_id,
        total_purchases=(user_data['total_purchases'] or 0) + calc['total_with_discount'],
        orders_count=(user_data['orders_count'] or 0) + 1,
        nickname=nickname,
        server=server
    )
    
    if promocode and promocode_id:
        use_promocode(promocode_id, user_id, order_id)
    
    referrer_id = get_referrer(user_id)
    if referrer_id:
        referral_bonus = calculate_referral_bonus(calc['total_with_discount'])
        if referral_bonus > 0:
            add_referral_bonus(referrer_id, user_id, order_id, referral_bonus)
    
    result_text = f"✨ Спасибо!\n\n📦 Заказ #{order_id}\n👤 Ник: {nickname}\n🌍 Сервер: {server}\n💰 Сумма: {calc['total_with_discount']}💵\n"
    
    if calc['discount_3plus'] > 0:
        result_text += f"🎁 Скидка (5%): -{calc['discount_3plus']}💵\n"
    if calc['promocode_discount'] > 0:
        result_text += f"🎟 Скидка по промокоду: -{calc['promocode_discount']}💵\n"
    
    result_text += f"🍀 Начислено Монет: {coins_earned}\n\nВаш заказ отправлен на проверку.\nПосле проверки Вы получите уведомление."
    
    await message.answer(result_text)
    
    user_carts[user_id] = []
    await state.clear()

# === БЫСТРАЯ ПОКУПКА ===

@router.callback_query(F.data.startswith("buy_now_"))
async def buy_now(callback: CallbackQuery):
    """Быстрая покупка товара"""
    product_id = int(callback.data.replace("buy_now_", ""))
    product = get_product_by_id(product_id)
    
    if not product:
        await callback.answer("Товар не найден")
        return
    
    if product["price_game"] is None:
        await callback.answer("Этот товар доступен только по предзаказу")
        return
    
    user_carts[callback.from_user.id] = [{"id": product_id, "name": product["name"], "price": product["price_game"], "quantity": 1}]
    
    await callback.answer("Товар добавлен в корзину")
    await callback.message.edit_text("💳 *Выберите способ оплаты:*", reply_markup=get_payment_methods_keyboard(), parse_mode="Markdown")

# === НАВИГАЦИЯ ===

@router.callback_query(F.data == "back_to_shop")
async def back_to_shop(callback: CallbackQuery):
    await show_shop(callback)

@router.callback_query(F.data == "back_to_cart")
async def back_to_cart(callback: CallbackQuery):
    await show_cart(callback)

@router.callback_query(F.data == "main_menu")
async def back_to_main_menu(callback: CallbackQuery):
    await callback.message.answer("🌸 *Добро пожаловать в SAKURA STORE!* 🌸\n\nВыберите интересующий раздел:", reply_markup=get_main_menu_keyboard(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "back_to_payment")
async def back_to_payment(callback: CallbackQuery):
    await checkout(callback)

@router.callback_query(F.data == "cancel_order")
async def cancel_order(callback: CallbackQuery):
    await callback.message.edit_text("❌ Заказ отменен", reply_markup=get_back_to_shop_keyboard())