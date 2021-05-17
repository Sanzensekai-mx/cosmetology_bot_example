import logging

from aiogram.dispatcher.filters import Text

from aiogram.types import Message
from keyboards.default import main_menu_client
from loader import dp


logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] '
                           u'#%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO)


@dp.message_handler(Text(equals=['О салоне']))
async def show_about(message: Message):
    logging.info(f'from: {message.chat.full_name}, text: {message.text.upper()}')
    await message.answer('Размещение информации о салоне, контакты, местоположение и т.д.',
                         reply_markup=main_menu_client)
