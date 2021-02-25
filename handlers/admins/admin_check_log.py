import logging
import datetime
import calendar
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, ReplyKeyboardRemove, InlineKeyboardMarkup, \
    InlineKeyboardButton, CallbackQuery, ContentType

from keyboards.default import main_menu_admin, main_menu_master
from keyboards.inline import check_logs_choice_range
from loader import dp
from states.admin_states import AdminCheckLog
from utils.db_api.models import DBCommands
from data.config import masters_and_id, admins

db = DBCommands()


def get_key(d, value):
    for k, v in d.items():
        if v == value:
            return k


logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] '
                           u'#%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO)


@dp.callback_query_handler(text_contains='cancel_check', chat_id=masters_and_id.values(), state=AdminCheckLog)
async def process_cancel_add_service(call: CallbackQuery, state: FSMContext):
    logging.info(f'from: {call.message.chat.full_name}, text: {call.message.text}, info: Отмена рассылки.')
    await call.answer(cache_time=60)
    if str(call.message.chat.id) in admins and str(call.message.chat.id) in masters_and_id.values():
        await call.message.answer('Отмена.', reply_markup=main_menu_admin)  # Добавить reply_markup
    else:
        await call.message.answer('Отмена.', reply_markup=main_menu_master)  # Вставить меню мастера
    await state.reset_state()


@dp.message_handler(Text(equals=['Посмотреть записи ко мне',
                                 'Посмотреть записи ко мне (супер-мастер)',
                                 'Посмотреть записи ко мне (мастер)']), chat_id=masters_and_id.values())
async def start_check_logs(message: Message):
    await message.answer('Просмотр записи клиентов.', reply_markup=check_logs_choice_range)
    await AdminCheckLog.ChoiceRange.set()


async def process_choice_time_callback(call, state):
    full_datetime = call.data.split('_')[1]
    master_username = get_key(masters_and_id, str(call.message.chat.id))
    log = await db.get_log_by_full_datetime(full_datetime,
                                            master_username)
    date = [int(d.strip()) for d in log.date.strip('()').split(',')]
    # День, месяц, год
    date_to = datetime.date(date[0], date[1], date[2])
    await call.message.answer(
        f'''
Время - {log.time}\n
Дата -  {date[2]} / {date[1]} / {date[0]}\n
Мастер - {log.name_master}\n
Клиент - {log.name_client}\n
Услуга - {log.service}''', reply_markup=ReplyKeyboardRemove())
    kb = InlineKeyboardMarkup()
    # написать callback
    kb.add(InlineKeyboardButton(f'Вернуться записям на {date[2]} число',
                                callback_data=f'back:to:time_{date_to}_{master_username}'))
    kb.add(InlineKeyboardButton('Отмена просмотра', callback_data='cancel_check'))
    await call.message.answer(f'{log.phone_number}', reply_markup=kb)


@dp.callback_query_handler(text_contains='back:to:time_', state=AdminCheckLog)
async def back_to_date_timetable(call: CallbackQuery, state: FSMContext):
    date = [int(i) for i in call.data.split('_')[1].split('-')]
    res = datetime.date(date[0], date[1], date[2])
    await process_choice_day(call, res, state)


@dp.callback_query_handler(text_contains='admin:datetime_', chat_id=masters_and_id.values(),
                           state=AdminCheckLog.CheckToday)
async def process_choice_time(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    await process_choice_time_callback(call, state)


@dp.callback_query_handler(text_contains='admin:datetime_', chat_id=masters_and_id.values(),
                           state=AdminCheckLog.CheckWeek)
async def process_choice_time(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await call.answer(cache_time=60)
    await process_choice_time_callback(call, state)
    # full_datetime = call.data.split('_')[1]
    # log = await db.get_log_by_full_datetime(full_datetime,
    #                                         get_key(masters_and_id, str(call.message.chat.id)))
    # date = log.date.strip('()').split(',')
    # await call.message.answer(f'Время - {log.time}'
    #                           f'\nДата - {date[2]}/{date[1]}/{date[0]}'
    #                           f'\nМастер - {log.name_master}'
    #                           f'\nКлиент - {log.name_client}'
    #                           f'\nУслуга - {log.service}')
    # await call.message.answer(f'{log.phone_number}')


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
                                                callback_data=f'admin:datetime_{datetime_with_weekdays} {log.time}'))
        kb_time.add(InlineKeyboardButton('Отмена просмотра', callback_data='cancel_check'))
        await call.message.answer(f'День: {day} '
                                  f'\nВыберите время записи, чтобы просмотреть кто записался.',
                                  reply_markup=kb_time)
    else:
        await call.message.answer('Никто не записывался на этот день.', reply_markup=check_logs_choice_range)
        await AdminCheckLog.ChoiceRange.set()
    
    # for num, log in enumerate(all_today_logs, 1):
    #     result_message_list.append(f'\n{log}. {log.time} - {log.name_client} - {log.service} - {log.phone_number}')
    #     result_message_list.append('\n')
    # await call.message.answer(all_today_logs)


async def process_choice_week(call, date_time, state):
    # await state.update_data('kb': None)
    # data = await state.get_data()
    current_date = date_time
    c = calendar.LocaleTextCalendar(calendar.MONDAY, locale='Russian_Russia')
    month_c = calendar.monthcalendar(current_date.year, current_date.month)
    print_month_c = c.formatmonth(current_date.year, current_date.month)
    # print(month_c)
    # Дни недели в текущей неделе
    # print([day for seq in month_c for day in seq if current_date.day in seq])
    current_week_days = [day for seq in month_c for day in seq if current_date.day in seq]
    # print(current_week_days)
    kb_week = InlineKeyboardMarkup(row_width=7)
    for week_day in [item for item in print_month_c.split()][2:9]:
        if week_day == 'Пн':
            kb_week.add(InlineKeyboardButton(week_day, callback_data=week_day))
            continue
        kb_week.insert(InlineKeyboardButton(week_day, callback_data=week_day))
    for day in current_week_days:
        if day < current_date.day:
            kb_week.insert(InlineKeyboardButton(' ', callback_data=f'wrong_date'))
            continue
        kb_week.insert(
            InlineKeyboardButton(day,
                                 callback_data=f'date_{current_date.year}, {current_date.month}, {day}'))
    kb_week.add(InlineKeyboardButton('Отмена просмотра', callback_data='cancel_check'))
    await state.update_data({'kb': kb_week})
    await call.message.answer('Выберите дату записи, '
                              'чтобы просмотреть кто записался на текущей неделе.',
                              reply_markup=kb_week)


@dp.callback_query_handler(state=AdminCheckLog.CheckWeek, text_contains='wrong_date')
async def wrong_date_process(call: CallbackQuery):
    await call.answer(cache_time=60)
    await call.message.answer('Дата неактуальна, выберите не пустую дату.')


@dp.callback_query_handler(state=AdminCheckLog.CheckWeek, text_contains='date_')
async def process_choice_day_of_week(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    # print(call.data.split('_')[1])
    date = [int(i) for i in call.data.split('_')[1].split(',')]
    # print(date)
    choice_day = datetime.date(date[0], date[1], date[2])
    await process_choice_day(call=call, date_time=choice_day, state=state)


@dp.callback_query_handler(state=AdminCheckLog.ChoiceRange, chat_id=masters_and_id.values(), text_contains='logs_')
async def choice_range_log(call: CallbackQuery, state: FSMContext):
    result = call.data.split('_')[1]
    await call.answer(cache_time=60)
    current_date = datetime.date.today()
    if result == 'today':
        await AdminCheckLog.CheckToday.set()
        await process_choice_day(call, current_date, state=state)
    elif result == 'week':
        await AdminCheckLog.CheckWeek.set()
        await process_choice_week(call, current_date, state=state)
    elif result == 'months':
        pass
