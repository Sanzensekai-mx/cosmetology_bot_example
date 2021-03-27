import locale
import logging
import pytz
import datetime
import calendar
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, ReplyKeyboardRemove, InlineKeyboardMarkup, \
    InlineKeyboardButton, CallbackQuery

from keyboards.default import main_menu_admin, main_menu_master
from keyboards.inline import check_logs_choice_range
from loader import dp
from states.admin_states import AdminCheckLog
from utils.db_api.models import DBCommands
from data.config import admins, masters_id, months, days, tz_ulyanovsk

db = DBCommands()


def get_key(d, value):
    for k, v in d.items():
        if v == value:
            return k


logging.basicConfig(format=u'%(filename)s 'u'[LINE:%(lineno)d] '
                           u'#%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO)


@dp.message_handler(commands=['time'])
async def show_time(message: Message):
    # tz = pytz.timezone('Europe/Ulyanovsk')
    current_date = datetime.datetime.now()
    await message.answer(f'\ntoday'
                         f'\n{current_date}'
                         f'\nutcnow'
                         f'\n{datetime.datetime.utcnow()}'
                         f'\nmaybe current'
                         f'\n{datetime.datetime.now(tz_ulyanovsk)}')
    # locale.setlocale(locale.LC_ALL, '')
    # locale.setlocale(locale.LC_ALL, 'ru_RU')
    # c = calendar.TextCalendar(calendar.MONDAY)
    # print_month_c = c.formatmonth(current_date.year, current_date.month)
    await message.answer(months)
    await message.answer(days)


@dp.callback_query_handler(text_contains='cancel_check', chat_id=masters_id, state=AdminCheckLog)
async def process_cancel_add_service(call: CallbackQuery, state: FSMContext):
    logging.info(f'from: {call.message.chat.full_name}, text: {call.message.text}, info: Отмена просмотра.')
    await call.answer(cache_time=60)
    if str(call.message.chat.id) in admins and str(call.message.chat.id) in masters_id:
        await call.message.answer('Отмена.', reply_markup=main_menu_admin)
    else:
        await call.message.answer('Отмена.', reply_markup=main_menu_master)
    await state.reset_state()


@dp.message_handler(Text(equals=['Посмотреть записи ко мне',
                                 'Посмотреть записи ко мне (супер-мастер)',
                                 'Посмотреть записи ко мне (мастер)']), chat_id=masters_id)
async def start_check_logs(message: Message):
    await message.answer('Просмотр записи клиентов.', reply_markup=check_logs_choice_range)
    # print(await db.get_master_and_id())
    await AdminCheckLog.ChoiceRange.set()


async def process_choice_time_callback(call):
    full_datetime = call.data.split('_')[1]
    master_username = get_key(await db.get_master_and_id(), str(call.message.chat.id))
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
    kb.add(InlineKeyboardButton(f'Вернуться к записям на {date[2]} число',
                                callback_data=f'back:to:time_{date_to}_{master_username}'))
    kb.add(InlineKeyboardButton('Отмена просмотра', callback_data='cancel_check'))
    await call.message.answer(f'{log.phone_number}', reply_markup=kb)


@dp.callback_query_handler(text_contains='back:to:time_', state=AdminCheckLog)
async def back_to_date_timetable(call: CallbackQuery):
    await call.answer(cache_time=60)
    date = [int(i) for i in call.data.split('_')[1].split('-')]
    res = datetime.date(date[0], date[1], date[2])
    await process_choice_day(call, res)


@dp.callback_query_handler(text_contains='admin:datetime_', chat_id=masters_id,
                           state=AdminCheckLog)
async def process_choice_time(call: CallbackQuery):
    await call.answer(cache_time=60)
    await process_choice_time_callback(call)


async def process_choice_day(call, date_time):
    current_date = date_time
    year, month, day = current_date.year, current_date.month, current_date.day
    c = calendar.TextCalendar(calendar.MONDAY)
    datetime_with_weekdays = [date for date in c.itermonthdays4(year, month) if date[2] == day][0]
    # today_datetime_log = await db.get_datetime()
    print(get_key(await db.get_master_and_id(), str(call.message.chat.id)))
    all_today_logs = await db.get_logs_only_date(f'{datetime_with_weekdays}',
                                                 get_key(await db.get_master_and_id(), str(call.message.chat.id)))
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
    c = calendar.TextCalendar(calendar.MONDAY)
    month_c = calendar.monthcalendar(current_date.year, current_date.month)
    print_month_c = c.formatmonth(current_date.year, current_date.month)
    # print(month_c)
    # Дни недели в текущей неделе
    # print([day for seq in month_c for day in seq if current_date.day in seq])
    current_week_days = [day for seq in month_c for day in seq if current_date.day in seq]
    # print(current_week_days)
    kb_week = InlineKeyboardMarkup(row_width=7)
    for week_day in [item for item in print_month_c.split()][2:9]:
        # if week_day == 'Mo':
        #     kb_week.add(InlineKeyboardButton(days.get(week_day), callback_data=days.get(week_day)))
        #     continue
        kb_week.insert(InlineKeyboardButton(days.get(week_day), callback_data=days.get(week_day)))
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


@dp.callback_query_handler(state=AdminCheckLog, text_contains='wrong_date')
async def wrong_date_process(call: CallbackQuery):
    await call.answer(cache_time=60)
    await call.message.answer('Дата неактуальна, выберите не пустую дату.')


@dp.callback_query_handler(state=AdminCheckLog.CheckWeek, text_contains='date_')
async def process_choice_day_of_week(call: CallbackQuery):
    await call.answer(cache_time=60)
    # print(call.data.split('_')[1])
    date = [int(i) for i in call.data.split('_')[1].split(',')]
    # print(date)
    choice_day = datetime.date(date[0], date[1], date[2])
    await process_choice_day(call=call, date_time=choice_day)


@dp.callback_query_handler(state=AdminCheckLog.CheckMonths, text_contains='date_')
async def process_choice_day_of_week(call: CallbackQuery):
    await call.answer(cache_time=60)
    # print(call.data.split('_')[1])
    date = [int(i.strip('()')) for i in call.data.split('_')[1].split(',')]
    # print(date)
    choice_day = datetime.date(date[0], date[1], date[2])
    await process_choice_day(call=call, date_time=choice_day)


@dp.callback_query_handler(state=AdminCheckLog.CheckMonths, text_contains='month_')
async def change_month_process(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    data = await state.get_data()
    current_date = datetime.date.today()
    result = call.data.split('_')[1]
    choice_year = data.get('current_choice_year')
    choice_month = data.get('current_choice_month')
    if result == 'next':
        if choice_month == 12:
            choice_year = current_date.year + 1
            choice_month = 1
        else:
            choice_month = int(choice_month) + 1
        data['current_choice_year'] = choice_year
        data['current_choice_month'] = choice_month
        await state.update_data()
        await process_choice_months(call, current_date, state,
                                    year=choice_year,
                                    month=choice_month,
                                    day=1)
    elif result == 'previous':
        if choice_month == 1:
            choice_year = choice_year - 1
            choice_month = 12
        else:
            choice_month = int(choice_month) - 1
        data['current_choice_year'] = choice_year
        data['current_choice_month'] = choice_month
        await state.update_data()
        await process_choice_months(call, current_date, state,
                                    year=choice_year,
                                    month=choice_month,
                                    day=1)


async def process_choice_months(call, date_time, state, year, month, day):
    data = await state.get_data()
    c = calendar.TextCalendar(calendar.MONDAY)
    current_date = date_time
    # year, month = current_date.year, current_date.month
    if month == current_date.month and year == current_date.year:
        month = current_date.month
        year = current_date.year
        day = current_date.day
    print_c = c.formatmonth(year, month)
    inline_calendar = InlineKeyboardMarkup(row_width=7)
    if (month != current_date.month and year == current_date.year) \
            or ((month != current_date.month or month == current_date.month)
                and year != current_date.year):
        inline_calendar.add(InlineKeyboardButton('<', callback_data='month_previous'))
    data['current_choice_month'] = month
    data['current_choice_year'] = year
    await state.update_data(data)
    inline_calendar.insert(InlineKeyboardButton(f'{months.get(print_c.split()[0])} {print_c.split()[1]}',
                                                callback_data=' '))
    inline_calendar.insert(InlineKeyboardButton('>', callback_data='month_next'))
    for week_day in print_c.split()[2:9]:
        if week_day == 'Mo':
            inline_calendar.add(InlineKeyboardButton(days.get(week_day), callback_data=days.get(week_day)))
            continue
        inline_calendar.insert(InlineKeyboardButton(days.get(week_day), callback_data=days.get(week_day)))
    for day_cal in c.itermonthdays4(year, month):
        # Исключает дни другого месяца, прошедшие дни и выходные дни (Суббота, Воскресенье)
        if day_cal[2] == 0 \
                or day > day_cal[2] \
                or day_cal[2] in [date[0] for date
                                  in c.itermonthdays2(year, month)
                                  if date[1] in [5, 6]] \
                or day_cal[1] != month:
            inline_calendar.insert(InlineKeyboardButton(' ', callback_data='wrong_date'))
            continue
        inline_calendar.insert(InlineKeyboardButton(day_cal[2], callback_data=f'date_{day_cal}'))
    inline_calendar.add(InlineKeyboardButton('Отмена просмотра', callback_data='cancel_check'))
    await call.message.answer('Выберите дату для просмотра записей.', reply_markup=inline_calendar)


@dp.callback_query_handler(state=AdminCheckLog.ChoiceRange, chat_id=masters_id, text_contains='logs_')
async def choice_range_log(call: CallbackQuery, state: FSMContext):
    result = call.data.split('_')[1]
    await call.answer(cache_time=60)
    current_date = datetime.date.today()
    if result == 'today':
        await AdminCheckLog.CheckToday.set()
        await process_choice_day(call, current_date)
    elif result == 'week':
        await AdminCheckLog.CheckWeek.set()
        await process_choice_week(call, current_date, state=state)
    elif result == 'months':
        await AdminCheckLog.CheckMonths.set()
        await state.update_data(
            {'current_choice_month': '',
             'current_choice_year': ''})
        await process_choice_months(call, current_date, state=state,
                                    year=current_date.year,
                                    month=current_date.month,
                                    day=current_date.day)
