import logging
import datetime
import calendar
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, ReplyKeyboardRemove, InlineKeyboardMarkup, \
    InlineKeyboardButton, CallbackQuery, ContentType

from keyboards.default import main_menu_client
from keyboards.inline import check_logs_choice_range
from loader import dp
from states.user_states import UserCheckLog
from utils.db_api.models import DBCommands
# from data.config import masters_and_id

db = DBCommands()

logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] '
                           u'#%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO)


@dp.message_handler(Text(equals='Мои записи'))
async def check_users_logs(message: Message, state: FSMContext):
    logging.info(f'from: {message.chat.first_name}, text: {message.text}')
    logs_list = await db.get_all_logs_by_user_id(message.chat.id)
    kb_logs = InlineKeyboardMarkup(row_width=5)
    print(logs_list[0].full_datetime)
    print(type(logs_list[0].full_datetime))
    for log in logs_list:
        # Список вида (2021, 2, 22, 0) 10:00
        date = [x.strip('()').strip() for x in log.date.split(',')]
        kb_logs.add(InlineKeyboardButton(f'Дата: {date[2]}/{date[1]}/{date[0]} Время: {log.time}',
                                         callback_data=f'user:datetime_{log.full_datetime}_{log.name_master}'))
    await message.answer('Ваши записи:', reply_markup=kb_logs)


@dp.callback_query_handler(text_contains='user:datetime_')
async def process_one_log(call: CallbackQuery):
    result = call.data.split('_')
    choice_log_datetime, choice_master = result[1], result[2]
    log = await db.get_log_by_full_datetime(choice_log_datetime, choice_master)
    date = log.date.strip('()').split(',')
    service = await db.get_service(log.service)
    await call.message.answer(f'Время - {log.time}'
                              f'\nДата - {date[2]}/{date[1]}/{date[0]}'
                              f'\nМастер - {choice_master}'
                              f'\nВаше имя - {log.name_client}'
                              f'\nУслуга - {log.service}'
                              f'\nСтоимость - {service.price}')
    # Добавить кнопку-ссылку на пост в инстаграмм об услуге или показать описание услуги
