import logging

from loader import dp
from aiogram.types import Message
from data.config import admins


@dp.message_handler(chat_id=admins, commands=['help_admin'])
async def admin_help(message: Message):
    logging.info(f'from: {message.chat.full_name}, text: {message.text}')
    text = [
        'Список команд администратора: ',
        '/mail - рассылка всем пользователям бота.',
        '/add_service - добавить услугу в БД.',
    ]
    await message.answer('\n'.join(text))
