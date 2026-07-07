# handlers/promocode.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.promocodes_db import check_promocode, use_promocode

router = Router()

class PromocodeStates(StatesGroup):
    waiting_for_promocode = State()

@router.callback_query(F.data == "enter_promocode")
async def enter_promocode(callback: CallbackQuery, state: FSMContext):
    """Запрос на ввод промокода"""
    await callback.message.edit_text(
        "🎟 *Введите промокод:*\n\n"
        "Отправьте код в чат.",
        parse_mode="Markdown"
    )
    await state.set_state(PromocodeStates.waiting_for_promocode)
    await callback.answer()

@router.message(PromocodeStates.waiting_for_promocode)
async def process_promocode(message: Message, state: FSMContext):
    """Обработка введенного промокода"""
    from handlers.shop import user_carts, format_cart_message
    
    user_id = message.from_user.id
    cart = user_carts.get(user_id, [])
    
    if not cart:
        await message.answer("❌ Ваша корзина пуста")
        await state.clear()
        return
    
    # Вычисляем текущую сумму
    total = sum(item["price"] * item["quantity"] for item in cart)
    items_count = sum(item["quantity"] for item in cart)
    
    # Проверяем промокод
    promocode = message.text.strip().upper()
    result = check_promocode(promocode, user_id, total)
    
    if not result["valid"]:
        await message.answer(result["message"])
        await state.clear()
        return
    
    # Сохраняем промокод в состоянии
    await state.update_data(
        promocode=promocode,
        promocode_id=result["promocode_id"],
        discount_percent=result["discount_percent"]
    )
    
    # Пересчитываем сумму с промокодом
    discount_3plus = 0
    if items_count >= 3:
        discount_3plus = total * 0.05
    
    promocode_discount = total * (result["discount_percent"] / 100)
    total_discount = int(discount_3plus + promocode_discount)
    total_with_discount = int(total - total_discount)
    
    # Показываем обновленную корзину
    cart_message = f"🎟 *Промокод применен!*\n\n"
    cart_message += f"Код: `{promocode}`\n"
    cart_message += f"Скидка: {result['discount_percent']}%\n\n"
    cart_message += format_cart_message(user_id)
    cart_message += f"\n\n🎟 Скидка по промокоду: -{int(promocode_discount)}💵"
    cart_message += f"\n💎 Итого к оплате: {total_with_discount}💵"
    
    from keyboards.shop_keyboards import get_cart_keyboard
    await message.answer(
        cart_message,
        parse_mode="Markdown"
    )
    
    await state.clear()