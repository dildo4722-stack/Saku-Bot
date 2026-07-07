from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

def get_shop_categories_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура с категориями магазина"""
    buttons = [
        [InlineKeyboardButton(text="⭐ Привилегии", callback_data="category_privileges")],
        [InlineKeyboardButton(text="❤️ Рубины", callback_data="category_rubins")],
        [InlineKeyboardButton(text="🧸 Питомцы", callback_data="category_pets")],
        [InlineKeyboardButton(text="🎁 Подарочные паки", callback_data="category_packs")],
        [InlineKeyboardButton(text="🎟 Подарочные сертификаты", callback_data="category_certificates")],
        [InlineKeyboardButton(text="🛒 Корзина", callback_data="cart")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_back_to_shop_keyboard() -> InlineKeyboardMarkup:
    """Кнопка возврата к категориям магазина"""
    buttons = [
        [InlineKeyboardButton(text="🔙 Назад к категориям", callback_data="back_to_shop")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# keyboards/shop_keyboards.py

def get_product_actions_keyboard(product_id: int, is_preorder: bool = False) -> InlineKeyboardMarkup:
    """Кнопки действий с товаром"""
    buttons = []
    
    if not is_preorder:
        buttons.append([InlineKeyboardButton(text="🛒 Добавить в корзину", callback_data=f"add_to_cart_{product_id}")])
        buttons.append([InlineKeyboardButton(text="💳 Оплатить сейчас", callback_data=f"buy_now_{product_id}")])
    
    buttons.append([InlineKeyboardButton(text="❌ Отменить", callback_data="back_to_shop")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_cart_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура управления корзиной"""
    buttons = [
        [InlineKeyboardButton(text="🎟 Ввести промокод", callback_data="enter_promocode")],
        [InlineKeyboardButton(text="💳 Оформить заказ", callback_data="checkout")],
        [InlineKeyboardButton(text="🗑 Очистить корзину", callback_data="clear_cart")],
        [InlineKeyboardButton(text="🔙 Продолжить покупки", callback_data="back_to_shop")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_promocode_skip_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для пропуска промокода"""
    buttons = [
        [InlineKeyboardButton(text="⏭ Пропустить", callback_data="skip_promocode")],
        [InlineKeyboardButton(text="🔙 Назад к оплате", callback_data="back_to_payment")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_payment_methods_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора способа оплаты"""
    buttons = [
        [InlineKeyboardButton(text="💵 Игровая валюта", callback_data="pay_game_currency")],
        [InlineKeyboardButton(text="⭐ Telegram Stars", callback_data="pay_telegram_stars")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_cart")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_servers_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора сервера"""
    buttons = [
        [InlineKeyboardButton(text="Сервер 1", callback_data="server_1")],
        [InlineKeyboardButton(text="Сервер 2", callback_data="server_2")],
        [InlineKeyboardButton(text="Сервер 3", callback_data="server_3")],
        [InlineKeyboardButton(text="Сервер 4", callback_data="server_4")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_payment")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_confirm_order_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура подтверждения заказа"""
    buttons = [
        [InlineKeyboardButton(text="✅ Подтвердить заказ", callback_data="confirm_order")],
        [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_order")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_payment_instructions_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура с инструкцией оплаты"""
    buttons = [
        [InlineKeyboardButton(text="✅ Я оплатил", callback_data="i_paid")],
        [InlineKeyboardButton(text="❌ Отменить заказ", callback_data="cancel_order")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_contact_manager_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для связи с менеджером"""
    buttons = [
        [InlineKeyboardButton(text="👤 Связаться с менеджером", url="https://t.me/Mik55554")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_payment")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)