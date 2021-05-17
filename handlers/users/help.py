import logging
from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandHelp

from loader import dp
from utils.misc import rate_limit


@rate_limit(5, 'help')
@dp.message_handler(CommandHelp())
async def bot_help(message: types.Message):
    logging.info(f'from: {message.chat.full_name}, text: {message.text.upper()}')
    text = [
        'Список команд: ',
        '/start - Начать',
        '/help - Получить справку'
    ]
    await message.answer('\n'.join(text))
