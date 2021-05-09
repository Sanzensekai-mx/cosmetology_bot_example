import datetime
import logging
from aiogram import types
from aiogram.dispatcher.filters import CommandStart

from keyboards.default import main_menu_client, main_menu_admin, main_menu_master
from loader import dp
from utils.db_api.models import DBCommands
from data.config import admins, masters_id, tz_ulyanovsk

logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] '
                           u'#%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO)

db = DBCommands()


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    user = await db.get_user(message.chat.id)
    if user is None:    # Если пользователя нет в БД
        logging.info(f'Новый пользователь (/start): Name: {message.chat.full_name}, '
                     f'chat_id: {message.chat.id}')
        user = await db.add_new_user()
    else:
        id_user = user.id
        logging.info(f'Зарегистрированный пользователь (/start): id: {id_user}, '
                     f'Name: {message.chat.full_name}, '
                     f'chat_id: {message.chat.id}')
    chat_id = user.user_id
    name_user = user.full_name
    count_users = await db.count_users()
    if str(chat_id) in admins:
        current_date = datetime.datetime.now(tz_ulyanovsk)
        await message.answer(f'''
Привет, {name_user}!
У тебя права администратора! Введи /help_admin
Пользователей в БД: {count_users} юзер(а).
Текущая дата: {current_date.day}/{current_date.month}/{current_date.year}
Текущее время: {current_date.hour}:{current_date.minute}
Ваш user_id:''', reply_markup=main_menu_admin)
        await message.answer(message.chat.id)
    elif str(chat_id) in masters_id and str(chat_id) not in admins:
        await message.answer(f'''
Привет, {name_user}!
У тебя права мастера салона!
                ''', reply_markup=main_menu_master)
    else:
        await message.answer(f'''
Привет, {name_user}!
''')
        await message.answer('Нажми кнопку ниже для того, чтобы начать!', reply_markup=main_menu_client)
