import logging
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, \
    CallbackQuery, ContentType

from keyboards.default import main_menu_admin
from loader import dp, bot
from states.admin_states import AdminDelMaster
from utils.db_api.models import DBCommands
from data.config import admins

db = DBCommands()


@dp.callback_query_handler(chat_id=admins, state=AdminDelMaster, text_contains='cancel_del_master')
async def process_cancel_del_master(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    logging.info(f'from: {call.message.chat.full_name}, text: {call.message.text}, info: Отмена удаления мастера.')
    await call.message.answer('Отмена удаления мастера.', reply_markup=main_menu_admin)
    await state.reset_state()


@dp.message_handler(Text(equals='Удалить мастера'), chat_id=admins)
async def start_del_master(message: Message):
    logging.info(f'from: {message.chat.full_name}, text: {message.text}')
    cancel_choice_master_to_del = InlineKeyboardMarkup()
    all_masters = await db.all_masters()
    for master in all_masters:
        cancel_choice_master_to_del.add(InlineKeyboardButton(f'{master.master_name}',
                                                             callback_data=f'm_{master.master_name}'))
    cancel_choice_master_to_del.add(InlineKeyboardButton('Отмена удаления',
                                                         callback_data='cancel_del_master'))
    await message.answer('Выберите мастера для удаления.', reply_markup=cancel_choice_master_to_del)
    await AdminDelMaster.Del.set()


@dp.callback_query_handler(chat_id=admins, state=AdminDelMaster.Del, text_contains='m_')
async def del_master(call: CallbackQuery, state: FSMContext):
    master_to_del = call.data.split('_')[1]
    master_item = await db.get_master(master_to_del)
    await db.del_master(master_to_del)
    await call.message.answer(f'Мастер {master_item.master_name} удален. \nНе забудьте удалить его '
                              f'chat_id из переменных в Dashboard Heroku.'
                              f'\nchat_id удаленного матера - {master_item.master_user_id}')
    await state.finish()
