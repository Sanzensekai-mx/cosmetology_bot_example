import logging
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, \
    CallbackQuery, ContentType

from keyboards.default import main_menu_admin
from keyboards.inline import cancel_add_master
from loader import dp, bot
from states.admin_states import AdminAddMaster
from utils.db_api.models import DBCommands
from data.config import admins
from handlers.users.appointment import return_kb_mes_services

db = DBCommands()


async def confirm_or_change(data, mes):
    kb_confirm = InlineKeyboardMarkup(row_width=4)
    for_kb_name_items = {'name': 'имя мастера', 'user_id': 'id мастера', 'services': 'список услуг'}
    for key in data.keys():
        if key in ['is_master_in_db', 'current_services_dict']:
            pass
        else:
            change_button = InlineKeyboardButton(f'Изменить {for_kb_name_items.get(key)}',
                                                 callback_data=f'change:{key}')
            kb_confirm.add(change_button)
    kb_confirm.add(InlineKeyboardButton('Подтвердить добавление', callback_data='сonfirm'))
    kb_confirm.add(InlineKeyboardButton('Отмена добавления мастера', callback_data='cancel_add_master'))
    await mes.answer(f'''
ВНИМАНИЕ. Если вы хотите обновить имя мастера,
то сначала удалите исходного мастера и добавьте вновь, вводя новые данные.
Проверьте введенные данные.\n
Имя мастера - {data.get("name")}\n
User_id - {data.get("user_id")}\n
Список услуг мастера - {data.get("services")}
''', reply_markup=kb_confirm)
    await AdminAddMaster.Confirm.set()


@dp.callback_query_handler(chat_id=admins, state=AdminAddMaster, text_contains='cancel_add_master')
async def process_cancel_add_master(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    logging.info(f'from: {call.message.chat.full_name}, text: {call.message.text}, info: Отмена добавления услуги.')
    await call.message.answer('Отмена добавления нового мастера.', reply_markup=main_menu_admin) # Добавить reply_markup
    await state.reset_state()


@dp.message_handler(Text(equals='Добавить мастера'), chat_id=admins)
async def start_add_master(message: Message, state: FSMContext):
    logging.info(f'from: {message.chat.full_name}, text: {message.text}')
    await message.answer('Введите имя нового мастера. \nИли существующего мастера (для обновления информации).'
                         '\nНажмите на кнопку ниже для отмены.',
                         reply_markup=cancel_add_master)
    await AdminAddMaster.Name.set()
    await state.update_data(
        {'name': '',
         'user_id': '',
         'services': [],
         'is_master_in_db': ''}
    )


@dp.message_handler(chat_id=admins, state=AdminAddMaster.Name)
async def add_name_master(message: Message, state: FSMContext):
    data = await state.get_data()
    if not data.get('name'):
        name = message.text.strip()
        data['name'] = name
        data['is_master_in_db'] = 'Мастер уже существует в БД.' if await db.is_this_master_in_db(name) \
            else 'Такого мастера нет в БД.'
        is_master_in_db = data.get('is_master_in_db')
        await state.update_data(data)
        await message.answer(f'Имя мастера: "{name}". '
                             f'\n{is_master_in_db}'
                             '\nПришлите user_id мастера.'
                             '\nПопросите вашего будущего мастера прописать команду /send_id. '
                             'Скопируйте полученный идентификатор и уже от своего лица отошлите боту.',
                             reply_markup=cancel_add_master)

        await AdminAddMaster.ID.set()
    else:
        name = message.text.strip()
        data['name'] = name
        await state.update_data(data)
        await confirm_or_change(data, message)


async def process_print_kb_mes(message, state, change_list=False):
    data = await state.get_data()
    mes_and_kb = await return_kb_mes_services(state=state, is_it_appointment=False)
    answer_mes = mes_and_kb[0]
    kb_services = mes_and_kb[1]
    kb_services.add(InlineKeyboardButton('Подтвердить список сервисов', callback_data='confirm_services'))
    kb_services.add(InlineKeyboardButton('Отмена добавления мастера',
                                         callback_data='cancel_add_master'))
    # await message.answer(text=answer_mes, reply_markup=kb_services)
    if change_list is False:
        await message.answer(f'Название: "{data.get("name")}". '
                             f'\nUser_id "{data.get("user_id")}".'
                             f'\nТекущий список услуг: '
                             f'\n{data.get("services")}'
                             f'\n{answer_mes}', reply_markup=kb_services)
    else:
        await message.answer('Пришлите новый список услуг для мастера.\n'
                             f'\nТекущий список услуг: '
                             f'\n{data.get("services")}'
                             f'\n{answer_mes}', reply_markup=kb_services)

    await AdminAddMaster.Services.set()


@dp.message_handler(chat_id=admins, state=AdminAddMaster.ID)
async def add_id_master(message: Message, state: FSMContext):
    data = await state.get_data()
    if not data.get('user_id'):
        user_id = message.text.strip()
        data['user_id'] = user_id
        await state.update_data(data)
        await process_print_kb_mes(message, state)
        await AdminAddMaster.Services.set()
    else:
        user_id = message.text
        data['user_id'] = user_id
        await state.update_data(data)
        await confirm_or_change(data, message)


@dp.callback_query_handler(chat_id=admins, state=AdminAddMaster.Services, text_contains='confirm_services')
async def confirm_master_service_list(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    await AdminAddMaster.Confirm.set()
    data = await state.get_data()
    await confirm_or_change(data=data, mes=call.message)


@dp.callback_query_handler(chat_id=admins, state=AdminAddMaster.Services, text_contains='s_')
async def process_add_services_to_master_list(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    # result_num_service = call.data.split('_')[1]
    result_name_service = call.data.split('_')[2]
    data = await state.get_data()
    data['services'].append(result_name_service)
    await state.update_data(data)
    await process_print_kb_mes(call.message, state)


@dp.callback_query_handler(text_contains='change', chat_id=admins, state=AdminAddMaster.Confirm)
async def change_some_data(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    data = await state.get_data()
    what_to_change = call.data.split(':')[1]
    if what_to_change == 'name':
        await call.message.answer('Введите новое имя мастера.')
        await AdminAddMaster.Name.set()
    elif what_to_change == 'user_id':
        await call.message.answer('Пришлите новый user_id мастера.')
        await AdminAddMaster.ID.set()
    elif what_to_change == 'services':
        data['services'].clear()
        await state.update_data(data)
        # await call.message.answer('Пришлите новый список услуг для мастера.')
        await process_print_kb_mes(message=call.message, state=state, change_list=True)
        await AdminAddMaster.Services.set()


@dp.callback_query_handler(text_contains='сonfirm', chat_id=admins, state=AdminAddMaster.Confirm)
async def confirm_new_meme(call: CallbackQuery, state: FSMContext):
    data_from_state = await state.get_data()
    await db.add_master(
        master_name=data_from_state.get("name"),
        master_user_id=data_from_state.get("user_id"),
        master_services='_'.join(data_from_state.get("services")),
    )
    await call.message.answer('Мастер добавлен.', reply_markup=main_menu_admin)
    await state.finish()