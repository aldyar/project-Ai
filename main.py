import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from app.database.models import async_main

from app.user import user
from app.admin import admin

from app.database.request import schedule_daily_task  # Импортируем функцию расписания
from apscheduler.schedulers.asyncio import AsyncIOScheduler

async def main():   
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_routers(admin,user)
    dp.startup.register(on_startup)

    scheduler = AsyncIOScheduler()
    schedule_daily_task(scheduler)  # Настраиваем задачи
    scheduler.start()  # Запускаем планировщик

    await dp.start_polling(bot)


async def on_startup(dispatcher):
    await async_main()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass


