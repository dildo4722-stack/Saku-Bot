# handlers/start.py
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, FSInputFile
import os

from config import BANNER_PATH
from keyboards.main_menu import get_main_menu_keyboard
from database.users_db import create_user
from database.admin_db import is_admin

# Создаем роутер для этого модуля
router = Router()

WELCOME_TEXT = (
    "🌸 Добро пожаловать в *SAKURA STORE*! 🌸\n\n"
    "Здесь вы можете приобрести игровые товары для серверов *MinePlanet*:\n"
    "💎 Привилегии\n"
    "🔮 Рубины\n"
    "🐾 Питомцы\n"
    "🎁 Подарочные паки\n"
    "📜 Сертификаты\n\n"
    "💵 Оплата игровой валютой\n"
    "⭐ Telegram Stars\n\n"
    "⸻\n"
    "Спасибо, что выбираете SAKURA STORE! ✨"
)

ADMIN_WELCOME_TEXT = (
    "🔑 *Админ-панель SAKURA STORE*\n\n"
    "Добро пожаловать, администратор!\n"
    "Выберите нужный раздел:"
)

# handlers/start.py (функция send_welcome_page)
async def send_welcome_page(message: Message):
    """Вспомогательная функция отправки главного экрана"""
    create_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )
    
    from database.admin_db import is_admin, get_admin_role
    
    admin = is_admin(message.from_user.id)
    role = get_admin_role(message.from_user.id) if admin else None
    keyboard = get_main_menu_keyboard(is_admin=admin, role=role)
    
    if admin:
        role_names = {"owner": "Владелец", "manager": "Менеджер", "moder": "Модератор"}
        welcome_text = f"🔑 *Админ-панель SAKURA STORE*\n\nРоль: {role_names.get(role, 'Админ')}\nВыберите раздел:"
    else:
        welcome_text = WELCOME_TEXT
    
    if os.path.exists(BANNER_PATH):
        banner = FSInputFile(BANNER_PATH)
        await message.answer_photo(photo=banner, caption=welcome_text, reply_markup=keyboard, parse_mode="Markdown")
    else:
        await message.answer(text=welcome_text, reply_markup=keyboard, parse_mode="Markdown")

@router.message(CommandStart())
async def cmd_start(message: Message):
    """Хендлер на команду /start"""
    await send_welcome_page(message)

@router.message(F.text == "🏠 Главное меню")
async def btn_main_menu(message: Message):
    """Хендлер для кнопки возврата в главное меню"""
    await send_welcome_page(message)