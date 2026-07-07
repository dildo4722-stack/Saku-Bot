import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers import start
from handlers import shop
from handlers import profile
from handlers import cashback
from handlers import referrals
from handlers import rules
from handlers import support
from handlers import exchange
from handlers import about
from handlers import orders
from handlers import promocode
from handlers import admin_full

async def main():
    # Настройка логирования в консоль
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )
    
    # Инициализация бота и диспетчера
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
   
    dp.include_router(referrals.router)  
    dp.include_router(start.router)      
    dp.include_router(shop.router)       
    dp.include_router(profile.router)    
    dp.include_router(cashback.router) 
    dp.include_router(rules.router)  
    dp.include_router(support.router)
    dp.include_router(exchange.router)
    dp.include_router(about.router)
    dp.include_router(orders.router)
    dp.include_router(promocode.router)
    dp.include_router(admin_full.router)
    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())