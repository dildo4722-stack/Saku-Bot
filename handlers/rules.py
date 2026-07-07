# handlers/rules.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.admin_settings import get_setting

router = Router()

RULES_TEXT = (
    "*📜 Правила SAKURA STORE*\n\n"
    
    "*1️⃣ Общие положения*\n"
    "Совершая покупку, вы автоматически соглашаетесь со всеми правилами магазина.\n"
    "Незнание правил не освобождает от ответственности.\n\n"
    
    "*2️⃣ Оплата*\n"
    "💵 Оплата игровой валютой принимается только на Первом сервере MinePlanet.\n"
    "⭐ Оплата Telegram Stars производится через Telegram.\n"
    "💰 Комиссия при переводе оплачивается покупателем.\n\n"
    
    "*3️⃣ Выдача товара*\n"
    "Перед оплатой внимательно укажите свой никнейм и сервер.\n"
    "Выдача товара осуществляется только после подтверждения оплаты.\n"
    "Если указан неверный ник или сервер, ответственность несет покупатель.\n\n"
    
    "*4️⃣ Возврат средств*\n"
    "После успешной выдачи товара возврат средств невозможен.\n"
    "Возврат возможен только в случае, если магазин не может выполнить заказ.\n\n"
    
    "*5️⃣ Срок работы магазина*\n"
    "🗓️ Магазин работает только первые 1,5 месяца после начала каждого вайпа.\n"
    "После окончания этого периода магазин закрывается до следующего вайпа.\n\n"
    
    "*6️⃣ Кэшбэк*\n"
    "❤️ За каждую покупку начисляются Монеты согласно таблице кэшбэка.\n"
    "♻️ После каждого нового вайпа все накопленные Монеты сгорают.\n"
    "Монеты нельзя обменять на игровую валюту или реальные деньги.\n\n"
    
    "*7️⃣ Реферальная система*\n"
    "Бонус начисляется только после успешной покупки приглашённого игрока.\n"
    "При подозрении на накрутку реферальные бонусы могут быть аннулированы.\n\n"
    
    "*8️⃣ Акции и скидки*\n"
    "🎉 Скидка 5% действует при покупке трёх и более товаров в одном заказе.\n"
    "Акции и скидки не суммируются, если не указано иное.\n\n"
    
    "*9️⃣ Обязанности покупателя*\n"
    "Не передавайте чек об оплате третьим лицам.\n"
    "Не пытайтесь обмануть администрацию магазина.\n"
    "Соблюдайте правила сервера MinePlanet.\n\n"
    
    "*🔟 Право администрации*\n"
    "Администрация вправе отказать в обслуживании при попытке мошенничества или нарушении правил.\n"
    "Администрация может изменять цены, акции и правила без предварительного уведомления.\n\n"
    
    "*1️⃣1️⃣ Важно*\n"
    "Магазин не связан с администрацией сервера MinePlanet и работает как отдельный магазин.\n"
    "Все спорные ситуации решаются через менеджера.\n\n"
    
    "*1️⃣2️⃣ Поддержка*\n"
    "По всем вопросам обращайтесь в тех поддержку: @Help\\_Sakura\\_Stor\\_bot"
)

def get_rules_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для правил"""
    buttons = [
        [InlineKeyboardButton(text="💬 Тех. поддержка", url="https://t.me/Help_Sakura_Stor_bot")],
        [InlineKeyboardButton(text="🛍 Перейти в магазин", callback_data="shop")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@router.message(F.text == "📜 Правила")
async def show_rules(message: Message):
    """Показывает правила из настроек"""
    rules_text = get_setting("rules_text", "")
    
    if not rules_text:
        rules_text = RULES_TEXT
    
    await message.answer(rules_text, reply_markup=get_rules_keyboard(), parse_mode="Markdown")

@router.callback_query(F.data == "rules")
async def show_rules_callback(callback: CallbackQuery):
    """Показывает правила через callback"""
    await callback.message.edit_text(
        RULES_TEXT,
        reply_markup=get_rules_keyboard(),
        parse_mode="Markdown",
        disable_web_page_preview=True
    )