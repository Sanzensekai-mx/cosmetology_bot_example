import logging
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, \
    CallbackQuery, ContentType

from keyboards.default import main_menu_admin, admin_default_cancel_confirm_service, admin_default_cancel_service, \
    admin_default_cancel_confirm_masters_list
from keyboards.inline import cancel_add_service
from loader import dp, bot
from states.admin_states import AdminAddService
from utils.db_api.models import DBCommands
from data.config import admins
from handlers.users.appointment import return_kb_masters

db = DBCommands()


async def confirm_or_change(data, mes):
    kb_confirm = InlineKeyboardMarkup(row_width=4)
    for key in data.keys():
        if key == 'is_service_in_db':
            pass
        else:
            change_button = InlineKeyboardButton(f'Изменить {key}', callback_data=f'change:{key}')
            kb_confirm.add(change_button)
    # kb_confirm.add(InlineKeyboardButton('Подтвердить', callback_data='сonfirm'))
    # kb_confirm.add(InlineKeyboardButton('Отмена', callback_data='cancel_add_service'))
    await mes.answer('Подтверждение добавления новой услуги.', reply_markup=admin_default_cancel_confirm_service)
    await mes.answer(f'''
ВНИМАНИЕ. Если вы хотите обновить название услугу,
то сначала удалите исходную услугу и добавьте новую, вводя новые данные.
Проверьте введенные данные.\n
Название - {data.get("name")}\n
Ссылка на картинку - {data.get("pic_file_id")}\n
Описание - {data.get("describe")}\n
Время оказание услуги - {data.get("time")}\n
Цена - {data.get("price")}\n
Мастера - {data.get("masters_list")}\n''', reply_markup=kb_confirm)
    await AdminAddService.Confirm.set()


@dp.callback_query_handler(chat_id=admins, state=AdminAddService, text_contains='cancel_add_service')
async def inline_process_cancel_add_service(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    logging.info(f'from: {call.message.chat.full_name}, text: {call.message.text}, info: Отмена добавления услуги.')
    await call.message.answer('Отмена добавления новой услуги.', reply_markup=main_menu_admin)  # Добавить reply_markup
    await state.reset_state()


@dp.message_handler(Text(equals=['Отмена добавления услуги']), chat_id=admins, state=AdminAddService)
async def default_process_cancel_add_service(message: Message, state: FSMContext):
    logging.info(f'from: {message.chat.full_name}, text: {message.text}, info: Отмена добавления услуги.')
    await message.answer('Отмена добавления новой услуги.', reply_markup=main_menu_admin)  # Добавить reply_markup
    await state.reset_state()


@dp.message_handler(Text(equals='Добавить услугу'), chat_id=admins)
async def start_add_service(message: Message, state: FSMContext):
    logging.info(f'from: {message.chat.full_name}, text: {message.text}')
    await message.answer('Название новой услуги.', reply_markup=ReplyKeyboardRemove())
    await message.answer('Введите название новой услуги или услуги, который уже существует, '
                         'но её данные необходимо обновить. '
                         '\nНажмите на кнопку ниже для отмены.',
                         reply_markup=cancel_add_service)
    await AdminAddService.Name.set()
    await state.update_data(
        {'name': '',
         'pic_file_id': '',
         'price': '',
         'time': '',
         'describe': '',
         'masters_list': [],
         'is_service_in_db': ''}
    )


@dp.message_handler(chat_id=admins, state=AdminAddService.Name)
async def add_name_service(message: Message, state: FSMContext):
    data = await state.get_data()
    if not data.get('name'):
        name = message.text.strip()
        data['name'] = name
        data['is_service_in_db'] = 'Услуга уже существует в БД.' if await db.is_this_service_in_db(name) \
            else 'Такой услуги нет в БД.'
        is_service_in_db = data.get('is_service_in_db')
        await state.update_data(data)
        await message.answer('Цена новой услуги.')
        await message.answer(f'Название: "{name}". '
                             f'\n{is_service_in_db}'
                             '\nПришлите цену услуги.',
                             reply_markup=cancel_add_service)

        await AdminAddService.Price.set()
    else:
        name = message.text.strip()
        data['name'] = name
        await state.update_data(data)
        await confirm_or_change(data, message)


@dp.message_handler(chat_id=admins, state=AdminAddService.Price)
async def add_price_service(message: Message, state: FSMContext):
    data = await state.get_data()
    if not data.get('price'):
        price = message.text
        data['price'] = price
        await state.update_data(data)
        await message.answer('Фото новой услуги.')
        await message.answer(f'Название: "{data.get("name")}". '
                             f'\n{data.get("is_meme_in_db")}'
                             f'\nЦена услуги: {price}'
                             '\nПришлите фотографию услуги.',
                             reply_markup=cancel_add_service)
        await AdminAddService.PicHref.set()
    else:
        price = message.text
        data['price'] = price
        await state.update_data(data)
        await confirm_or_change(data, message)


# ДОДУМАТЬ ЭТУ ХРЕНЬ ИЛИ ВООБЩЕ УБРАТЬ
@dp.message_handler(chat_id=admins, state=AdminAddService.PicHref, content_types=[ContentType.PHOTO])
async def add_price_service(message: Message, state: FSMContext):
    data = await state.get_data()
    if not data.get('pic_file_id'):
        pic = message.photo[-1].file_id
        data['pic_file_id'] = pic
        await state.update_data(data)
        await message.answer('Время на оказание новой услуги.')
        await message.answer(f'Название: "{data.get("name")}". '
                             f'\n{data.get("is_meme_in_db")}'
                             f'\nЦена услуги: {data.get("price")}'
                             '\nНапишите время на оказание услуги. (В разработке или нет)',
                             reply_markup=cancel_add_service)
        await AdminAddService.Time.set()
    else:
        pic = message.text
        data['pic_file_id'] = pic
        await state.update_data(data)
        await confirm_or_change(data, message)


@dp.message_handler(chat_id=admins, state=AdminAddService.Time)
async def add_price_service(message: Message, state: FSMContext):
    data = await state.get_data()
    if not data.get('time'):
        time = message.text
        data['time'] = time
        await state.update_data(data)
        await message.answer('Описание новой услуги.')
        await message.answer(f'Название: "{data.get("name")}". '
                             f'\n{data.get("is_meme_in_db")}'
                             f'\nЦена услуги: {data.get("price")}'
                             f'\nВремя оказание услуги: {data.get("time")}'
                             '\nНапишите краткое описание услуги.',
                             reply_markup=cancel_add_service)
        await AdminAddService.Describe.set()
    else:
        time = message.text
        data['time'] = time
        await state.update_data(data)
        await confirm_or_change(data, message)


async def print_masters_choice(message, state, change_list=False):
    data = await state.get_data()
    choice_master = InlineKeyboardMarkup()
    all_masters = await db.all_masters()
    for master in all_masters:
        # split так как в БД хранится строка типа Ресницы_Волосы. Костыль херли
        choice_master.add(InlineKeyboardButton(f'{master.master_name}',
                                               callback_data=f'm_{master.master_name}'))
    await message.answer('Мастера, которые могут оказывать новую услугу.',
                         reply_markup=admin_default_cancel_confirm_masters_list)
    if change_list is False:
        await message.answer(f'Название: "{data.get("name")}". '
                             f'\nЦена услуги: {data.get("price")}'
                             f'\nВремя оказание услуги: {data.get("time")}'
                             f'\nТекущий список мастеров: '
                             f'\n{data.get("masters_list")}', reply_markup=choice_master)
    else:
        await message.answer('Пришлите новый список услуг для мастера.\n'
                             f'\nТекущий список мастеров: '
                             f'\n{data.get("masters_list")}', reply_markup=choice_master)
    await AdminAddService.Masters.set()


@dp.message_handler(chat_id=admins, state=AdminAddService.Describe)
async def add_price_service(message: Message, state: FSMContext):
    data = await state.get_data()
    if not data.get('describe'):
        describe = message.text
        data['describe'] = describe
        await state.update_data(data)
        await print_masters_choice(message=message, state=state)
        await AdminAddService.Masters.set()
    else:
        describe = message.text
        data['describe'] = describe
        await state.update_data(data)
        await confirm_or_change(data, message)


@dp.message_handler(Text(equals=['Подтвердить список мастеров']), chat_id=admins, state=AdminAddService.Masters)
async def confirm_masters_to_service_list(message: Message, state: FSMContext):
    # @dp.callback_query_handler(chat_id=admins, state=AdminAddMaster.Services, text_contains='confirm_services')
    # async def confirm_master_service_list(call: CallbackQuery, state: FSMContext):
    #     await call.answer(cache_time=60)
    await AdminAddService.Confirm.set()
    data = await state.get_data()
    await confirm_or_change(data=data, mes=message)


@dp.callback_query_handler(chat_id=admins, state=AdminAddService.Masters, text_contains='m_')
async def process_add_masters_to_service_list(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    result_name_master = call.data.split('_')[1]
    data = await state.get_data()
    data['masters_list'].append(result_name_master)
    await state.update_data(data)
    await print_masters_choice(call.message, state)


@dp.callback_query_handler(text_contains='change', chat_id=admins, state=AdminAddService.Confirm)
async def change_some_data(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    data = await state.get_data()
    what_to_change = call.data.split(':')[1]
    if what_to_change == 'name':
        await call.message.answer('Введите новое имя услуги', reply_markup=ReplyKeyboardRemove())
        await AdminAddService.Name.set()
    elif what_to_change == 'pic_file_id':
        await call.message.answer('Пришлите новое фото услуги')
        await AdminAddService.PicHref.set()
    elif what_to_change == 'describe':
        await call.message.answer('Пришлите новое описание услуги', reply_markup=ReplyKeyboardRemove())
        await AdminAddService.Describe.set()
    elif what_to_change == 'price':
        await call.message.answer('Пришлите новую цену услуги', reply_markup=ReplyKeyboardRemove())
        await AdminAddService.Price.set()
    elif what_to_change == 'time':
        await call.message.answer('Пришлите новое время оказания услуги', reply_markup=ReplyKeyboardRemove())
        await AdminAddService.Time.set()
    elif what_to_change == 'masters_list':
        data['masters_list'].clear()
        await state.update_data(data)
        await print_masters_choice(message=call.message, state=state, change_list=True)
        await AdminAddService.Masters.set()


# @dp.callback_query_handler(text_contains='сonfirm', chat_id=admins, state=AdminAddService.Confirm)
# async def confirm_new_meme(call: CallbackQuery, state: FSMContext):
@dp.message_handler(Text(equals=['Подтвердить добавление услуги']), chat_id=admins, state=AdminAddService.Confirm)
async def confirm_new_service(message: Message, state: FSMContext):
    data_from_state = await state.get_data()
    await db.add_service(
        service_name=data_from_state.get("name"),
        service_describe=data_from_state.get("describe"),
        service_pic_file_id=data_from_state.get("pic_file_id"),
        service_price=data_from_state.get("price"),
        service_time=int(data_from_state.get("time"))
    )
    masters = await db.all_masters()
    for master in masters:
        if master.master_name in data_from_state.get("masters_list"):
            name, m_id, user_id, master_services = master.master_name, master.id, \
                                                   master.master_user_id, master.master_services
            master_services.append(data_from_state.get("name"))
            await db.del_master(master.master_name)
            await db.add_master(
                master_name=name,
                master_user_id=user_id,
                master_services=master_services
            )
    await message.answer('Услуга добавлена.', reply_markup=main_menu_admin)
    # Тест отправки
    # pic = await db.show_service_test()
    # await bot.send_photo(chat_id=591763264, photo=pic.pic_file_id)
    await state.finish()
