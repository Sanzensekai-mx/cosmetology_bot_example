import logging

from aiogram import Dispatcher

from data.config import admins
from keyboards.default.main_menu import main_menu_admin


async def on_startup_notify(dp: Dispatcher):
    for admin in admins:
        logging.info('Отправлено сообщение "Бот запущен"')
        try:
            await dp.bot.send_message(admin, "Бот Запущен", reply_markup=main_menu_admin)

        except Exception as err:
            logging.exception(err)
