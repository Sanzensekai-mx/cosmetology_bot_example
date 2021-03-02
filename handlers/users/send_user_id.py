import logging
from aiogram import types
from aiogram.dispatcher.filters import CommandStart

from keyboards.default import main_menu_client, main_menu_admin, main_menu_master
from loader import dp, bot
from utils.db_api.models import DBCommands
from data.config import admins

logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] '
                           u'#%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO)


@dp.message_handler(commands=['send_id'])
async def send_user_id(message: types.Message):
    logging.info('Введена команда /send_id')
    for admin in admins:
        await bot.send_message(chat_id=admin, text=f'Пользователь {message.chat.full_name}'
                                                   f'\nchat_id:')
        await bot.send_message(chat_id=admin, text=message.chat.id)
