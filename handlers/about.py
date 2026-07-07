# handlers/about.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.admin_settings import get_setting

router = Router()

def get_about_text() -> str:
    """Формирует текст 'О магазине' с актуальными настройками"""
    mortal_nick = get_setting("mortal_nickname", "MortalKhan95290")
    manager = get_setting("manager_username", "@Mik55554")
    shop_name = get_setting("shop_name", "SAKURA STORE")
    
    # Проверяем, есть ли сохраненный текст в настройках
    custom_text = get_setting("about_text", "")
    if custom_text:
        return custom_text
    
    # Текст по умолчанию
    return (
        f"ℹ️ *О магазине*\n\n"
        f"*{shop_name}* 🌸 — независимый магазин игровых товаров "
        f"для серверов *MinePlanet*.\n"
        f"Здесь можно приобрести привилегии, рубины, питомцев, "
        f"подарочные паки и сертификаты.\n\n"
        
        f"⸻\n\n"
        
        f"*Способы оплаты:*\n\n"
        f"💵 *Игровая валюта MinePlanet*\n"
        f"Оплата принимается только на *Первом сервере* "
        f"переводом на аккаунт `{mortal_nick}`.\n\n"
        f"⭐ *Telegram Stars*\n"
        f"Оформление через менеджера.\n\n"
        
        f"⸻\n\n"
        
        f"*Время работы:*\n"
        f"Магазин работает только в течение *первых 1,5 месяцев* "
        f"после начала каждого вайпа.\n"
        f"После окончания этого периода оформление заказов "
        f"временно недоступно до начала следующего вайпа.\n"
        f"⚠️ *Бывают исключения*.\n\n"
        
        f"⸻\n\n"
        
        f"*Кэшбэк:*\n"
        f"После каждой подтверждённой покупки начисляются "
        f"*Монеты 🍀*, которые можно обменять на товары "
        f"и Telegram-подарки.\n"
        f"♻️ После каждого нового вайпа все накопленные "
        f"Монеты сгорают.\n\n"
        
        f"⸻\n\n"
        
        f"*Контакты:*\n"
        f"👤 Менеджер: {manager}\n"
        f"💬 Тех-поддержка: @Help_Sakura_Stor_bot\n\n"
        
        f"По всем вопросам, связанным с оформлением заказа, "
        f"оплатой или выдачей товаров, обращайтесь к менеджеру."
    )

def get_about_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для раздела 'О магазине'"""
    manager = get_setting("manager_username", "@Mik55554")
    # Убираем @ из username для ссылки
    manager_link = manager.replace("@", "")
    
    buttons = [
        [InlineKeyboardButton(text="👤 Написать менеджеру", url=f"https://t.me/{manager_link}")],
        [InlineKeyboardButton(text="💬 Тех. поддержка", url="https://t.me/Help_Sakura_Stor_bot")],
        [InlineKeyboardButton(text="📜 Правила", callback_data="rules")],
        [InlineKeyboardButton(text="🛍 Перейти в магазин", callback_data="shop")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@router.message(F.text == "ℹ️ О магазине")
async def show_about(message: Message):
    """Показывает информацию о магазине"""
    await message.answer(
        get_about_text(),
        reply_markup=get_about_keyboard(),
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

@router.callback_query(F.data == "about")
async def show_about_callback(callback: CallbackQuery):
    """Показывает информацию о магазине через callback"""
    await callback.message.edit_text(
        get_about_text(),
        reply_markup=get_about_keyboard(),
        parse_mode="Markdown",
        disable_web_page_preview=True
    )