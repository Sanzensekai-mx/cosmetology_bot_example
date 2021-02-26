import asyncio
from utils.db_api.database import create_db
from utils.del_old_logs import del_old_logs


async def on_startup(dp):
    import filters
    import middlewares
    filters.setup(dp)
    middlewares.setup(dp)
    asyncio.create_task(del_old_logs())

    from utils.notify_admins import on_startup_notify
    await on_startup_notify(dp)
    await create_db()

if __name__ == '__main__':
    from aiogram import executor
    from handlers import dp

    executor.start_polling(dp, on_startup=on_startup)
