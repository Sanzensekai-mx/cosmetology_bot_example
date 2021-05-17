import logging

from loader import dp
from aiogram.types import Message
from data.config import admins


@dp.message_handler(chat_id=admins, commands=['help_admin'])
async def admin_help(message: Message):
    logging.info(f'from: {message.chat.full_name}, text: {message.text.upper()}')
    text = [
        'Тут ничего нет',
    ]
    await message.answer('\n'.join(text))
