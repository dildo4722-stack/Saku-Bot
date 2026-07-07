# handlers/support.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

SUPPORT_TEXT = (
    "🎧 *Поддержка SAKURA STORE*\n\n"
    "Если у вас возникли вопросы или проблемы, "
    "вы можете обратиться в нашу службу поддержки:\n\n"
    "💬 *Техническая поддержка:*\n"
    "@Help\\_Sakura\\_Stor\\_bot\n\n"
    "👤 *Менеджер:*\n"
    "@Mik55554\n\n"
    "⸻\n\n"
    "Нажмите на кнопку ниже, чтобы связаться с нужным специалистом."
)

def get_support_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для раздела поддержки"""
    buttons = [
        [InlineKeyboardButton(text="💬 Тех. поддержка", url="https://t.me/Help_Sakura_Stor_bot")],
        [InlineKeyboardButton(text="👤 Написать менеджеру", url="https://t.me/Mik55554")],
        [InlineKeyboardButton(text="🛍 Перейти в магазин", callback_data="shop")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@router.message(F.text == "👤 Поддержка")
async def show_support(message: Message):
    """Показывает раздел поддержки"""
    await message.answer(
        SUPPORT_TEXT,
        reply_markup=get_support_keyboard(),
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

@router.callback_query(F.data == "support")
async def show_support_callback(callback: CallbackQuery):
    """Показывает поддержку через callback"""
    await callback.message.edit_text(
        SUPPORT_TEXT,
        reply_markup=get_support_keyboard(),
        parse_mode="Markdown",
        disable_web_page_preview=True
    )