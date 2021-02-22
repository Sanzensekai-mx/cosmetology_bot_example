import logging
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, \
    CallbackQuery, ContentType

from keyboards.default import main_menu_client
from keyboards.inline import cancel_add_service
from loader import dp, bot
from states.admin_states import AdminAddService
from utils.db_api.models import DBCommands
from data.config import admins

db = DBCommands()


async def confirm_or_change(data, mes):
    kb_confirm = InlineKeyboardMarkup(row_width=4)
    for key in data.keys():
        if key == 'is_service_in_db':
            pass
        else:
            change_button = InlineKeyboardButton(f'Изменить {key}', callback_data=f'change:{key}')
            kb_confirm.add(change_button)
    kb_confirm.add(InlineKeyboardButton('Подтвердить', callback_data='сonfirm'))
    kb_confirm.add(InlineKeyboardButton('Отмена', callback_data='cancel_add_service'))
    await mes.answer(f'''
ВНИМАНИЕ. Если вы хотите обновить название услугу,
то сначала удалите исходный усгу и введите новые данные.
\n/cancel_meme для отмены Добавления/Изменения мема. 
Проверьте введенные данные.\n
Название - {data.get("name")}\n
Ссылка на картинку - {data.get("pic_file_id")}\n
Описание - {data.get("describe")}\n
Время оказание услуги - {data.get("time")}\n
Цена - {data.get("price")}\n''', reply_markup=kb_confirm)
    await AdminAddService.Confirm.set()


@dp.callback_query_handler(chat_id=admins, state=AdminAddService, text_contains='cancel_add_service')
async def process_cancel_add_service(call: CallbackQuery, state: FSMContext):
    logging.info(f'from: {call.message.chat.full_name}, text: {call.message.text}, info: Отмена добавления услуги.')
    await call.message.answer('Отмена добавления новой услуги.', )  # Добавить reply_markup
    await state.reset_state()


@dp.message_handler(Text(equals='Добавить услугу'), chat_id=admins)
async def start_add_service(message: Message, state: FSMContext):
    logging.info(f'from: {message.chat.full_name}, text: {message.text}')
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


@dp.message_handler(chat_id=admins, state=AdminAddService.PicHref, content_types=[ContentType.PHOTO])
async def add_price_service(message: Message, state: FSMContext):
    data = await state.get_data()
    if not data.get('pic_href'):
        pic = message.photo[-1].file_id
        data['pic_file_id'] = pic
        await state.update_data(data)
        await message.answer(f'Название: "{data.get("name")}". '
                             f'\n{data.get("is_meme_in_db")}'
                             f'\nЦена услуги: {data.get("price")}'
                             '\nПришлите время на оказание услуги.',
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
        await message.answer(f'Название: "{data.get("name")}". '
                             f'\n{data.get("is_meme_in_db")}'
                             f'\nЦена услуги: {data.get("price")}'
                             f'\nВремя оказание услуги: {data.get("time")}'
                             '\nПришлите описание услуги.',
                             reply_markup=cancel_add_service)
        await AdminAddService.Describe.set()
    else:
        time = message.text
        data['time'] = time
        await state.update_data(data)
        await confirm_or_change(data, message)


@dp.message_handler(chat_id=admins, state=AdminAddService.Describe)
async def add_price_service(message: Message, state: FSMContext):
    data = await state.get_data()
    describe = message.text
    data['describe'] = describe
    await state.update_data(data)
    await confirm_or_change(data, message)


@dp.callback_query_handler(text_contains='change', chat_id=admins, state=AdminAddService.Confirm)
async def change_some_data(call: CallbackQuery):
    await call.answer(cache_time=60)
    what_to_change = call.data.split(':')[1]
    if what_to_change == 'name':
        await call.message.answer('Введите новое имя услуги')
        await AdminAddService.Name.set()
    elif what_to_change == 'pic_file_id':
        await call.message.answer('Пришлите новое фото услуги')
        await AdminAddService.PicHref.set()
    elif what_to_change == 'describe':
        await call.message.answer('Пришлите новое описание услуги')
        await AdminAddService.Describe.set()
    elif what_to_change == 'price':
        await call.message.answer('Пришлите новую цену услуги')
        await AdminAddService.Price.set()
    elif what_to_change == 'time':
        await call.message.answer('Пришлите новое время оказания услуги')
        await AdminAddService.Time.set()


@dp.callback_query_handler(text_contains='сonfirm', chat_id=admins, state=AdminAddService.Confirm)
async def confirm_new_meme(call: CallbackQuery, state: FSMContext):
    data_from_state = await state.get_data()
    await db.add_service(
        service_name=data_from_state.get("name"),
        service_describe=data_from_state.get("describe"),
        service_pic_file_id=data_from_state.get("pic_file_id"),
        service_price=data_from_state.get("price"),
        service_time=int(data_from_state.get("time"))
    )
    await call.message.answer('Услуга добавлена.', reply_markup=ReplyKeyboardRemove())  # Добавить reply_markup
    # Тест отправки
    # pic = await db.show_service_test()
    # await bot.send_photo(chat_id=591763264, photo=pic.pic_file_id)
    await state.finish()
