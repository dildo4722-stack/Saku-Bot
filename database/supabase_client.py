# database/supabase_client.py
"""
Читает баланс монет из Supabase (та же база, что использует мини-приложение
SAKU TAP), чтобы бот мог показывать общий баланс = монеты магазина + монеты
из мини-игры.
"""
import logging
import aiohttp

from config import SUPABASE_URL, SUPABASE_KEY

_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
}


async def get_supabase_coins(telegram_id: int) -> int:
    """Возвращает баланс монет игрока в SAKU TAP (0, если не найден/ошибка)."""
    url = f"{SUPABASE_URL}/rest/v1/users"
    params = {
        "select": "coins",
        "telegram_id": f"eq.{telegram_id}",
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url, params=params, headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=5),
            ) as resp:
                if resp.status != 200:
                    logging.warning(
                        "Supabase: неожиданный статус %s при запросе монет для %s",
                        resp.status, telegram_id,
                    )
                    return 0
                data = await resp.json()
                if data:
                    return int(data[0].get("coins") or 0)
                return 0
    except Exception as e:
        logging.error("Не удалось получить баланс монет из Supabase: %s", e)
        return 0


async def get_combined_coins(telegram_id: int, bot_coins: int) -> int:
    """Баланс монет магазина (SQLite) + баланс монет из SAKU TAP (Supabase)."""
    supabase_coins = await get_supabase_coins(telegram_id)
    return (bot_coins or 0) + supabase_coins