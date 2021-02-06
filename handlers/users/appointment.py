import logging
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.default import main_menu_no_orders
from loader import dp
from states.user_states import UserAppointment
from utils.db_api.models import DBCommands
from data.config import admins

db = DBCommands()

logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] '
                           u'#%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO)


async def confirm_or_change(data, mes):
    kb_confirm = InlineKeyboardMarkup(row_width=4)
    for key in data.keys():
        if key == 'is_meme_in_db':
            break
        change_button = InlineKeyboardButton(f'Изменить {key}', callback_data=f'change:{key}')
        kb_confirm.add(change_button)
    kb_confirm.add(InlineKeyboardButton('Подтвердить', callback_data='сonfirm'))
    await mes.answer(f'''
ВНИМАНИЕ. Если вы хотите обновить название мема,
то сначала удалите исходный мем и введите новые данные.
\n/cancel_meme для отмены Добавления/Изменения мема. 
Проверьте введенные данные.\n
Название - {data.get("name")}\n
Ссылка на картинку - {data.get("pic_href")}\n
Описание - {data.get("describe")}\n
Ссылка - {data.get("meme_href")}\n''', reply_markup=kb_confirm)
    await AdminNewMeme.Confirm.set()


@dp.message_handler(chat_id=admins, commands=['cancel_appointment'], state=UserAppointment)
async def cancel_mail(message: Message, state: FSMContext):
    logging.info(f'from: {message.chat.full_name}, text: {message.text}, info: Отмена рассылки.')
    await message.answer('Отмена рассылки.', reply_markup=main_menu_no_orders)
    await state.reset_state()


@dp.message_handler(Text(equals=['Запись']))
async def open_appointment_start(message: Message, state: FSMContext):
    logging.info(f'from: {message.chat.first_name}, text: {message.text}')
    # LOG you!!!!!!!
    await message.answer('Введите своё фамилию и имя.',
                         reply_markup=ReplyKeyboardRemove())
    await UserAppointment.AppointmentSetService.set()
    await state.update_data(
        {'name': '',
         'service': '',
         'master': '',
         'date': '',
         'time': ''
         }
    )


@dp.message_handler(state=UserAppointment.AppointmentSetName)
async def open_appointment_enter_name(message: Message, state: FSMContext):
    data = await state.get_data()
    if not data.get('name'):
        name = message.text.strip()
        data['name'] = name
        data['is_meme_in_db'] = 'Мем уже существует в БД.' if await db.is_this_meme_in_db(name) \
            else 'Такого мема нет в БД.'
        is_meme_in_db = data.get('is_meme_in_db')
        await state.update_data(data)
        await message.answer(f'Ваше Фамилия и Имя: "{name}". '
                             '\nВыберите услугу:', )

        await UserAppointment.AppointmentSetService.set()
    else:
        name = message.text.strip()
        data['name'] = name
        await state.update_data(data)
        await confirm_or_change(data, message)


# @dp.message_handler(state=UserAppointment.AppointmentSetService)
# async def open_appointment_enter_service(message: Message, state: FSMContext):
#     data = await state.get_data()
#     if not data.get('service'):
#          = message.text.strip()
#         data['service'] = name
#         data['is_meme_in_db'] = 'Запись на ваше имя уже существует.' if await db.is_this_meme_in_db(name) \
#             else 'Такого мема нет в БД.'
#         is_meme_in_db = data.get('is_meme_in_db')
#         await state.update_data(data)
#         await message.answer('Выберите мастера')
#
#         await UserAppointment.AppointmentSetMaster.set()
#     else:
#         name = message.text.strip()
#         data['name'] = name
#         await state.update_data(data)
#         await confirm_or_change(data, message)


@dp.message_handler(state=UserAppointment.AppointmentSetMaster)
async def open_appointment_enter_master():
    pass
