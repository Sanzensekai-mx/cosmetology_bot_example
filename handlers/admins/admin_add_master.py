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

db = DBCommands()


async def confirm_or_change(data, mes):
    kb_confirm = InlineKeyboardMarkup(row_width=4)
    for key in data.keys():
        if key == 'is_master_in_db':
            pass
        else:
            change_button = InlineKeyboardButton(f'Изменить {key}', callback_data=f'change:{key}')
            kb_confirm.add(change_button)
    kb_confirm.add(InlineKeyboardButton('Подтвердить добавление', callback_data='сonfirm'))
    kb_confirm.add(InlineKeyboardButton('Отмена добавления мастера', callback_data='cancel_add_master'))
    await mes.answer(f'''
ВНИМАНИЕ. Если вы хотите обновить имя мастера,
то сначала удалите исходного мастера и добавьте вновь, вводя новые данные.
Проверьте введенные данные.\n
Имя мастера - {data.get("name")}\n
Ссылка на картинку - {data.get("pic_file_id")}\n
Описание - {data.get("describe")}\n
Время оказание услуги - {data.get("time")}\n
Цена - {data.get("price")}\n''', reply_markup=kb_confirm)
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
         'service': [],
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


@dp.message_handler(chat_id=admins, state=AdminAddMaster.ID)
async def add_id_master(message: Message, state: FSMContext):
    data = await state.get_data()
    if not data.get('user_id'):
        user_id = message.text.strip()
        data['user_id'] = user_id
        await state.update_data(data)
        await message.answer(f'Название: "{data.get("name")}". '
                             f'\n{data.get("is_meme_in_db")}'
                             f'\nUser_id {data.get("user_id")}'
                             '\nВвод сервисов...',
                             reply_markup=cancel_add_master)
        await AdminAddMaster.Services.set()
    else:
        user_id = message.text
        data['user_id'] = user_id
        await state.update_data(data)
        await confirm_or_change(data, message)


@dp.message_handler(chat_id=admins, state=AdminAddMaster.Services)
async def add_services_master(message: Message, state: FSMContext):
    data = await state.get_data()
    services = db.all_services()
    await message.answer('Разработка...')
    # if not data.get('time'):
    #     time = message.text
    #     data['time'] = time
    #     await state.update_data(data)
    #     await message.answer(f'Название: "{data.get("name")}". '
    #                          f'\n{data.get("is_meme_in_db")}'
    #                          f'\nЦена услуги: {data.get("price")}'
    #                          f'\nВремя оказание услуги: {data.get("time")}'
    #                          '\nПришлите описание услуги.',
    #                          reply_markup=cancel_add_service)
    #     await AdminAddService.Describe.set()
    # else:
    #     time = message.text
    #     data['time'] = time
    #     await state.update_data(data)
    #     await confirm_or_change(data, message)