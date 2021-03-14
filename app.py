import asyncio
from utils.db_api.database import create_db
from utils.del_old_logs import del_old_logs
from utils.send_request import send_request


async def on_startup(dp):
    import filters
    import middlewares
    filters.setup(dp)
    middlewares.setup(dp)
    from utils.notify_admins import on_startup_notify
    await on_startup_notify(dp)
    # Создание задачи на удаление старых записей
    asyncio.create_task(del_old_logs())
    # Задача на отправку запроса каждые 5 минут
    asyncio.create_task(send_request())
    await create_db()

if __name__ == '__main__':
    from aiogram import executor
    from handlers import dp

    executor.start_polling(dp, on_startup=on_startup)
