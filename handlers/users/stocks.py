import logging

from aiogram.dispatcher.filters import Text

from aiogram.types import Message
from keyboards.default import main_menu_no_orders
from loader import dp


logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] '
                           u'#%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO)


@dp.message_handler(Text(equals=['Акции']))
async def show_about(message: Message):
    logging.info('Stocks show')
    await message.answer('Акции...'
                         '\n...'
                         '\n...',
                         reply_markup=main_menu_no_orders)

# Добавление акций через панель администратора, сохранение в бд?
