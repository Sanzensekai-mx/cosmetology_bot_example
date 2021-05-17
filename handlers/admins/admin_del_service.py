import logging
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from keyboards.default import main_menu_admin, admin_default_cancel_del_service
from loader import dp
from states.admin_states import AdminDelService
from utils.db_api.models import DBCommands
from data.config import admins
from utils.general_func import return_kb_mes_services

db = DBCommands()


@dp.callback_query_handler(chat_id=admins, state=AdminDelService, text_contains='cancel_del_service')
async def inline_process_cancel_del_service(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    await call.message.answer('Отмена удаления услуги.', reply_markup=main_menu_admin)
    await state.reset_state()


@dp.message_handler(Text(equals=['Отмена удаления услуги']), chat_id=admins, state=AdminDelService)
async def default_process_cancel_del_service(message: Message, state: FSMContext):
    await message.answer('Отмена удаления.', reply_markup=main_menu_admin)
    await state.reset_state()


@dp.message_handler(Text(equals='Удалить услугу'), chat_id=admins)
async def start_del_service(message: Message, state: FSMContext):
    logging.info(f'from: {message.chat.full_name}, text: {message.text.upper()}')
    services_mes, services_kb = await return_kb_mes_services(state=state)
    await message.answer('Удаление услуги.', reply_markup=admin_default_cancel_del_service)
    await message.answer(f'Выберите услугу для удаления.'
                         f'{services_mes}', reply_markup=services_kb)
    # cancel_choice_service_to_del = InlineKeyboardMarkup()
    # all_services = await db.all_services()
    # for service in all_services:
    #     cancel_choice_service_to_del.add(InlineKeyboardButton(f'{service.name}',
    #                                                           callback_data=f's_{service.name}'))
    # # cancel_choice_service_to_del.add(InlineKeyboardButton('Отмена удаления',
    # #                                                       callback_data='cancel_del_service'))
    # await message.answer('Удаление услуги.', reply_markup=admin_default_cancel_del_service)
    # await message.answer('Выберите услугу для удаления.', reply_markup=cancel_choice_service_to_del)
    await AdminDelService.Del.set()


@dp.callback_query_handler(chat_id=admins, state=AdminDelService.Del, text_contains='s_')
async def del_service(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    data = await state.get_data()
    service_num_to_del = call.data.split('_')[1]
    service_obj = await db.del_service(data.get('current_services_dict')[service_num_to_del])
    service_to_del = service_obj.name
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
    await call.message.answer(f'Услуга \'{service_to_del}\' удалена.', reply_markup=main_menu_admin)
    await state.finish()
