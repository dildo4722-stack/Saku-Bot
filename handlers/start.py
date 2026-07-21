# handlers/start.py
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
import os

from config import BANNER_PATH
from keyboards.main_menu import get_main_menu_keyboard
from database.users_db import create_user, get_user
from database.admin_db import is_admin, get_admin_role
from database.referrals_db import add_referral, get_referrer

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

# ===== НОВАЯ ФУНКЦИЯ: ОБРАБОТКА РЕФЕРАЛА =====
async def process_referral(user_id: int, referrer_id: int, username: str = None, first_name: str = None) -> bool:
    """Обрабатывает реферала: проверяет и сохраняет"""
    try:
        # Проверяем, что пользователь не приглашает сам себя
        if user_id == referrer_id:
            return False
        
        # Проверяем, существует ли реферер
        referrer = get_user(referrer_id)
        if not referrer:
            return False
        
        # Проверяем, не приглашен ли уже пользователь
        existing_referrer = get_referrer(user_id)
        if existing_referrer:
            return False
        
        # Создаем пользователя с реферером
        create_user(
            user_id=user_id,
            username=username,
            first_name=first_name,
            last_name=None,
            referrer_id=referrer_id
        )
        
        # Добавляем реферальную связь
        success = add_referral(referrer_id, user_id)
        
        if success:
            # Увеличиваем счетчик у реферера (если есть функция)
            # update_referral_count(referrer_id)
            return True
        
        return False
    except Exception as e:
        print(f"Ошибка обработки реферала: {e}")
        return False

async def send_welcome_page(message: Message, referrer_id: int = None):
    """Вспомогательная функция отправки главного экрана"""
    # Создаем пользователя (или обновляем)
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
    
    # ===== ДОБАВЛЯЕМ КНОПКУ С МИНИ-ПРИЛОЖЕНИЕМ =====
    # Если есть реферал, передаем его в Mini App
    web_app_url = "https://dildo4722-stack.github.io/tapsakutap/"  
    if referrer_id:
        web_app_url += f"?ref={referrer_id}"
    
    # Создаем клавиатуру с кнопкой Mini App
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
    
    # Берем существующую клавиатуру и добавляем кнопку
    # Если это админ, показываем админ-меню без дополнительной кнопки
    if not admin:
        # Создаем Inline-клавиатуру с кнопкой Mini App
        inline_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🌸 Открыть игру",
                        web_app=WebAppInfo(url=web_app_url)
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="👥 Пригласить друзей",
                        callback_data="invite_friends"
                    )
                ]
            ]
        )
        
        # Отправляем с Inline-клавиатурой
        if os.path.exists(BANNER_PATH):
            banner = FSInputFile(BANNER_PATH)
            await message.answer_photo(
                photo=banner,
                caption=welcome_text,
                reply_markup=inline_keyboard,
                parse_mode="Markdown"
            )
        else:
            await message.answer(
                text=welcome_text,
                reply_markup=inline_keyboard,
                parse_mode="Markdown"
            )
    else:
        # Для админа показываем обычное меню
        if os.path.exists(BANNER_PATH):
            banner = FSInputFile(BANNER_PATH)
            await message.answer_photo(
                photo=banner,
                caption=welcome_text,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
        else:
            await message.answer(
                text=welcome_text,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )

@router.message(CommandStart())
async def cmd_start(message: Message):
    """Хендлер на команду /start"""
    # Извлекаем реферальный ID из команды
    # Формат: /start ref7242502677 или /start ref_7242502677
    referrer_id = None
    args = message.text.split()
    
    if len(args) > 1:
        param = args[1]
        if param.startswith('ref'):
            try:
                # Убираем 'ref' или 'ref_'
                ref_str = param.replace('ref_', '').replace('ref', '')
                referrer_id = int(ref_str)
            except ValueError:
                pass
    
    # Если есть реферал и это не сам пользователь
    if referrer_id and referrer_id != message.from_user.id:
        # Проверяем, есть ли уже реферал у пользователя
        existing_referrer = get_referrer(message.from_user.id)
        
        if not existing_referrer:
            # Проверяем, существует ли реферер
            referrer = get_user(referrer_id)
            if referrer:
                # Создаем пользователя с реферером
                create_user(
                    user_id=message.from_user.id,
                    username=message.from_user.username,
                    first_name=message.from_user.first_name,
                    last_name=message.from_user.last_name,
                    referrer_id=referrer_id
                )
                # Добавляем реферальную связь
                add_referral(referrer_id, message.from_user.id)
                
                # Отправляем уведомление о реферале
                await message.answer(
                    f"🎉 Вы присоединились по приглашению!\n"
                    f"Пригласивший получит бонус за ваши покупки."
                )
                
                # Уведомляем реферера
                try:
                    await message.bot.send_message(
                        chat_id=referrer_id,
                        text=f"🎉 *Новый реферал!*\n\n"
                             f"Пользователь {message.from_user.first_name} "
                             f"присоединился по вашей ссылке!",
                        parse_mode="Markdown"
                    )
                except Exception as e:
                    print(f"Не удалось уведомить реферера: {e}")
    
    # Показываем приветствие с переданным рефералом
    await send_welcome_page(message, referrer_id)

@router.message(F.text == "🏠 Главное меню")
async def btn_main_menu(message: Message):
    """Хендлер для кнопки возврата в главное меню"""
    await send_welcome_page(message)
