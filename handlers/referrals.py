# handlers/referrals.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, CommandObject

from database.referrals_db import (
    add_referral, get_user_referrals, get_referrer, 
    get_total_referral_bonus
)
from database.users_db import get_user, create_user

router = Router()

def get_referral_link(user_id: int) -> str:
    """Генерирует реферальную ссылку"""
    from config import BOT_USERNAME
    return f"https://t.me/{BOT_USERNAME}?start=ref{user_id}"

def get_referral_keyboard(user_id: int):
    """Создает клавиатуру для реферальной системы"""
    buttons = [
        [InlineKeyboardButton(text="📋 Мои рефералы", callback_data="my_referrals")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="referral_stats")],
        [InlineKeyboardButton(text="👤 Личный кабинет", callback_data="profile")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@router.message(F.text == "👥 Реферальная система")
async def show_referral(message: Message):
    """Показывает реферальную систему"""
    user_data = get_user(message.from_user.id)
    
    if not user_data:
        await message.answer("❌ Сначала используйте /start")
        return
    
    referral_link = get_referral_link(message.from_user.id)
    total_bonus = get_total_referral_bonus(message.from_user.id)
    
    message_text = (
        f"👥 *Реферальная система*\n\n"
        f"🎁 Приглашайте друзей и получайте бонусы!\n\n"
        f"📋 *Ваша реферальная ссылка:*\n"
        f"`{referral_link}`\n\n"
        f"💰 *Условия:*\n"
        f"• За каждую покупку реферала вы получаете *2%* от суммы\n"
        f"• Бонус начисляется в Монетах 🍀\n"
        f"• Монеты можно обменять на товары\n\n"
        f"📊 *Ваша статистика:*\n"
        f"👥 Приглашено: {user_data['referrals_count'] or 0}\n"
        f"💰 Заработано: {total_bonus} 🍀\n\n"
        f"💡 *Как это работает:*\n"
        f"1. Отправьте ссылку другу\n"
        f"2. Друг запускает бота по вашей ссылке\n"
        f"3. После покупки друга вы получаете 2% бонуса\n"
    )
    
    await message.answer(
        message_text,
        reply_markup=get_referral_keyboard(message.from_user.id),
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "my_referrals")
async def show_my_referrals(callback: CallbackQuery):
    """Показывает список рефералов"""
    referrals = get_user_referrals(callback.from_user.id)
    
    if not referrals:
        message_text = "👥 *Мои рефералы*\n\nУ вас пока нет приглашенных пользователей."
    else:
        message_text = f"👥 *Мои рефералы* ({len(referrals)})\n\n"
        
        for i, ref in enumerate(referrals, 1):
            name = ref['first_name'] or ref['username'] or 'Пользователь'
            purchases = ref['total_purchases'] or 0
            bonus = ref['bonus_earned'] or 0
            
            message_text += (
                f"{i}. {name}\n"
                f"   💰 Покупок: {purchases}💵\n"
                f"   🍀 Бонус: {bonus} 🍀\n\n"
            )
    
    buttons = [
        [InlineKeyboardButton(text="🔙 Назад", callback_data="referral_back")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback.message.edit_text(
        message_text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "referral_stats")
async def show_referral_stats(callback: CallbackQuery):
    """Показывает статистику рефералов"""
    referrals = get_user_referrals(callback.from_user.id)
    total_bonus = get_total_referral_bonus(callback.from_user.id)
    
    active_referrals = sum(1 for ref in referrals if (ref['total_purchases'] or 0) > 0)
    
    message_text = (
        f"📊 *Статистика рефералов*\n\n"
        f"👥 Всего рефералов: {len(referrals)}\n"
        f"🟢 Активных (с покупками): {active_referrals}\n"
        f"💰 Всего заработано: {total_bonus} 🍀\n\n"
        f"💡 *Активные рефералы* — те, кто совершил хотя бы одну покупку."
    )
    
    buttons = [
        [InlineKeyboardButton(text="🔙 Назад", callback_data="referral_back")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback.message.edit_text(
        message_text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "referral_back")
async def referral_back(callback: CallbackQuery):
    """Возврат в реферальное меню"""
    user_data = get_user(callback.from_user.id)
    referral_link = f"https://t.me/SakuraStoreBot?start=ref{callback.from_user.id}"
    total_bonus = get_total_referral_bonus(callback.from_user.id)
    
    message_text = (
        f"👥 *Реферальная система*\n\n"
        f"🎁 Приглашайте друзей и получайте бонусы!\n\n"
        f"📋 *Ваша реферальная ссылка:*\n"
        f"`{referral_link}`\n\n"
        f"📊 *Статистика:*\n"
        f"👥 Приглашено: {user_data['referrals_count'] or 0}\n"
        f"💰 Заработано: {total_bonus} 🍀\n"
    )
    
    await callback.message.edit_text(
        message_text,
        reply_markup=get_referral_keyboard(callback.from_user.id),
        parse_mode="Markdown"
    )

# handlers/referrals.py (исправленный обработчик)

@router.message(CommandStart(deep_link=True, magic=F.args.regexp(r"ref\d+")))
async def start_with_referral(message: Message, command: CommandObject):
    """Обработчик старта с реферальной ссылкой"""
    # Получаем ID реферера из ссылки
    args = command.args
    
    if args and args.startswith('ref'):
        try:
            referrer_id = int(args[3:])  # Убираем 'ref'
            
            # Проверяем, что это не сам пользователь
            if referrer_id != message.from_user.id:
                # Проверяем, существует ли реферер
                referrer = get_user(referrer_id)
                if not referrer:
                    await message.answer("❌ Реферальная ссылка недействительна")
                    from handlers.start import send_welcome_page
                    await send_welcome_page(message)
                    return
                
                # Проверяем, не был ли уже приглашен этот пользователь
                existing_referrer = get_referrer(message.from_user.id)
                if existing_referrer:
                    await message.answer("⚠️ Вы уже были приглашены другим пользователем")
                    from handlers.start import send_welcome_page
                    await send_welcome_page(message)
                    return
                
                # Создаем нового пользователя с реферером
                create_user(
                    user_id=message.from_user.id,
                    username=message.from_user.username,
                    first_name=message.from_user.first_name,
                    last_name=message.from_user.last_name,
                    referrer_id=referrer_id
                )
                
                # Добавляем реферальную связь
                success = add_referral(referrer_id, message.from_user.id)
                
                if success:
                    # Отправляем приветствие с упоминанием бонуса
                    await message.answer(
                        f"🌸 *Добро пожаловать в SAKURA STORE!* 🌸\n\n"
                        f"Вы присоединились по реферальной ссылке!\n"
                        f"Совершайте покупки и получайте бонусы 🍀\n\n"
                        f"Пригласивший вас получит 2% от ваших покупок.",
                        parse_mode="Markdown"
                    )
                    
                    # Уведомляем реферера
                    try:
                        await message.bot.send_message(
                            chat_id=referrer_id,
                            text=f"🎉 *Новый реферал!*\n\n"
                                 f"Пользователь {message.from_user.full_name} "
                                 f"присоединился по вашей ссылке!\n"
                                 f"Вы будете получать 2% от его покупок.",
                            parse_mode="Markdown"
                        )
                    except Exception as e:
                        print(f"Не удалось уведомить реферера: {e}")
                    
                    # Показываем главное меню
                    from handlers.start import send_welcome_page
                    await send_welcome_page(message)
                    return
                else:
                    await message.answer("⚠️ Этот пользователь уже является вашим рефералом")
                    from handlers.start import send_welcome_page
                    await send_welcome_page(message)
                    return
                    
        except ValueError:
            await message.answer("❌ Неверный формат реферальной ссылки")
    
    # Если что-то пошло не так, обычный старт
    from handlers.start import send_welcome_page
    await send_welcome_page(message)