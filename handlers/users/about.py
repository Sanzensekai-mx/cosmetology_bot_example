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
    logging.info('About show')
    await message.answer('Размещение информации о салоне, контакты, местоположение и т.д.',
                         reply_markup=main_menu_client)
