import logging
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from keyboards.default import main_menu_admin
from loader import dp
from states.admin_states import AdminDelService
from utils.db_api.models import DBCommands
from data.config import admins

db = DBCommands()


@dp.callback_query_handler(chat_id=admins, state=AdminDelService, text_contains='cancel_del_service')
async def process_cancel_del_service(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    logging.info(f'from: {call.message.chat.full_name}, text: {call.message.text}, info: Отмена удаления услуги.')
    await call.message.answer('Отмена удаления услуги.', reply_markup=main_menu_admin)
    await state.reset_state()


@dp.message_handler(Text(equals='Удалить услугу'), chat_id=admins)
async def start_del_service(message: Message):
    logging.info(f'from: {message.chat.full_name}, text: {message.text}')
    cancel_choice_service_to_del = InlineKeyboardMarkup()
    all_services = await db.all_services()
    for service in all_services:
        cancel_choice_service_to_del.add(InlineKeyboardButton(f'{service.name}',
                                                              callback_data=f's_{service.name}'))
    cancel_choice_service_to_del.add(InlineKeyboardButton('Отмена удаления',
                                                          callback_data='cancel_del_service'))
    await message.answer('Выберите услугу для удаления.', reply_markup=cancel_choice_service_to_del)
    await AdminDelService.Del.set()


@dp.callback_query_handler(chat_id=admins, state=AdminDelService.Del, text_contains='s_')
async def del_service(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    service_to_del = call.data.split('_')[1]
    await db.del_service(service_to_del)
    masters = await db.all_masters()
    for master in masters:
        if service_to_del in master.master_services:
            name, m_id, user_id, master_services = master.master_name, master.id, \
                                                   master.master_user_id, master.master_services
            master_services.remove(service_to_del)
            await db.del_master(master.master_name)
            await db.add_master(
                master_name=name,
                master_user_id=user_id,
                master_services=master_services
            )
    await call.message.answer(f'Услуга \'{service_to_del}\' удалена.')
    await state.finish()
