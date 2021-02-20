import logging
import datetime
import calendar
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, ReplyKeyboardRemove, InlineKeyboardMarkup, \
    InlineKeyboardButton, CallbackQuery, ContentType

from keyboards.default import main_menu_no_orders
from keyboards.inline import check_logs_choice_range
from loader import dp
from states.admin_states import AdminCheckLog
from utils.db_api.models import DBCommands
from data.config import masters_and_id

db = DBCommands()


def get_key(d, value):
    for k, v in d.items():
        if v == value:
            return k


logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] '
                           u'#%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO)


@dp.message_handler(commands=['check_logs'], chat_id=masters_and_id.values())
async def start_check_logs(message: Message):
    await message.answer('Просмотр записи клиентов.', reply_markup=check_logs_choice_range)
    await AdminCheckLog.ChoiceRange.set()


@dp.callback_query_handler(text_contains='datetime_', chat_id=masters_and_id.values(), state=AdminCheckLog.CheckToday)
async def process_choice_time(call: CallbackQuery, state: FSMContext):
    full_datetime = call.data.split('_')[1]
    log = await db.get_log_by_full_datetime(full_datetime,
                                            get_key(masters_and_id, str(call.message.chat.id)))
    date = log.date.strip('()').split(',')
    await call.message.answer(f'Время - {log.time}'
                              f'\nДата - {date[0]} {date[1]} {date[2]}'
                              f'\nМастер - {log.name_master}'
                              f'\nКлиент - {log.name_client}'
                              f'\nУслуга - {log.service}')
    await call.message.answer(f'{log.phone_number}')
    # ВРЕМЕННО!!!!!!!!!!!!
    # await state.finish()


async def process_choice_day(call, date_time, state):
    current_date = date_time
    year, month, day = current_date.year, current_date.month, current_date.day
    c = calendar.LocaleTextCalendar(calendar.MONDAY, locale='Russian_Russia')
    datetime_with_weekdays = [date for date in c.itermonthdays4(year, month) if date[2] == day][0]
    # today_datetime_log = await db.get_datetime()
    all_today_logs = await db.get_logs_only_date(f'{datetime_with_weekdays}',
                                                 get_key(masters_and_id, str(call.message.chat.id)))
    # result_message_list = []
    if all_today_logs:
        kb_time = InlineKeyboardMarkup(row_width=5)
        for log in all_today_logs:
            kb_time.insert(InlineKeyboardButton(f'{log.time}',
                                                callback_data=f'datetime_{datetime_with_weekdays} {log.time}'))
        await call.message.answer('Выберите время записи, чтобы просмотреть кто записался.', reply_markup=kb_time)
    else:
        await call.message.answer('Никто не записывался на этот день.')
        await state.finish()
    
    # for num, log in enumerate(all_today_logs, 1):
    #     result_message_list.append(f'\n{log}. {log.time} - {log.name_client} - {log.service} - {log.phone_number}')
    #     result_message_list.append('\n')
    # await call.message.answer(all_today_logs)


@dp.callback_query_handler(state=AdminCheckLog.ChoiceRange, chat_id=masters_and_id.values(), text_contains='logs_')
async def choice_range_log(call: CallbackQuery, state: FSMContext):
    result = call.data.split('_')[1]
    await call.answer(cache_time=60)
    if result == 'today':
        current_date = datetime.date.today()
        await AdminCheckLog.CheckToday.set()
        await process_choice_day(call, current_date, state=state)
    elif result == 'week':
        pass
    elif result == 'months':
        pass
