import logging
import datetime
import calendar
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, InlineKeyboardMarkup, \
    InlineKeyboardButton, CallbackQuery

from keyboards.default import main_menu_admin, main_menu_master, admin_default_cancel_check_log, \
    admin_default_cancel_back_check_log, admin_default_cancel_2_back_check_log_month, \
    admin_default_cancel_2_back_check_log_week
from keyboards.inline import check_logs_choice_range
from loader import dp, bot
from states.admin_states import AdminCheckLog, AdminDelLog
from utils.db_api.models import DBCommands
from data.config import admins, masters_id, months, days
from utils.general_func import get_key, date_process_enter

db = DBCommands()

logging.basicConfig(format=u'%(filename)s 'u'[LINE:%(lineno)d] '
                           u'#%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO)


@dp.message_handler(commands=['time'])
async def show_time(message: Message):
    # tz = pytz.timezone('Europe/Ulyanovsk')
    current_date = datetime.datetime.now()
    await message.answer(f'\ntoday'
                         f'\n{current_date}'
                         f'\nutc_now'
                         f'\n{datetime.datetime.utcnow()}'
                         f'\nmaybe current'
                         f'\n{datetime.datetime.now()}')
    # f'\n{datetime.datetime.now(tz_ulyanovsk)}'
    # locale.setlocale(locale.LC_ALL, '')
    # locale.setlocale(locale.LC_ALL, 'ru_RU')
    # c = calendar.TextCalendar(calendar.MONDAY)
    # print_month_c = c.formatmonth(current_date.year, current_date.month)
    await message.answer(months)
    await message.answer(days)


@dp.callback_query_handler(text_contains='cancel_check', chat_id=masters_id, state=AdminCheckLog)
async def inline_process_cancel_master_check_logs(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    if str(call.message.chat.id) in admins and str(call.message.chat.id) in masters_id:
        await call.message.answer('Отмена.', reply_markup=main_menu_admin)
    else:
        await call.message.answer('Отмена.', reply_markup=main_menu_master)
    await state.reset_state()


@dp.message_handler(Text(equals='Отмена просмотра'), chat_id=masters_id, state=AdminCheckLog)
async def default_process_cancel_master_check_logs(message: Message, state: FSMContext):
    # await call.answer(cache_time=60)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 2)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    if str(message.chat.id) in admins and str(message.chat.id) in masters_id:
        await message.answer('Отмена.', reply_markup=main_menu_admin)
    else:
        await message.answer('Отмена.', reply_markup=main_menu_master)
    await state.reset_state()


@dp.message_handler(Text(equals='Назад в главное меню просмотра записей'), chat_id=masters_id, state=AdminCheckLog)
async def default_process_back_master_check_logs(message: Message):
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 2)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    await message.answer('Записи клиентов.', reply_markup=admin_default_cancel_check_log)
    await message.answer('Просмотр записи клиетов.', reply_markup=check_logs_choice_range)
    await AdminCheckLog.ChoiceRange.set()


@dp.message_handler(Text(equals='Назад к выбору даты (месяц)'), chat_id=masters_id,
                    state=AdminCheckLog)
async def process_back_to_calendar(message: Message, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 2)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    await message.answer('Записи по месяцам', reply_markup=admin_default_cancel_back_check_log)
    await date_process_enter(message=message,
                             state=state,
                             year=data.get('current_choice_year'),
                             month=data.get('current_choice_month'),
                             day=1, service=False)
    await AdminCheckLog.CheckMonths.set()


@dp.message_handler(Text(equals='Назад к выбору даты (неделя)'), chat_id=masters_id, state=AdminCheckLog)
async def process_back_to_calendar(message: Message, state: FSMContext):
    # current_date = datetime.datetime.now()
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 2)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    await process_choice_week(message=message, state=state)
    await AdminCheckLog.CheckWeek.set()


@dp.message_handler(Text(equals=['Посмотреть записи ко мне',
                                 'Посмотреть записи ко мне (супер-мастер)',
                                 'Посмотреть записи ко мне (мастер)']), chat_id=masters_id)
async def start_check_logs(message: Message, state: FSMContext):
    logging.info(f'from: {message.chat.full_name}, text: {message.text.upper()}')
    await message.answer('Записи клиентов.', reply_markup=admin_default_cancel_check_log)
    await message.answer('Просмотр записи клиентов.', reply_markup=check_logs_choice_range)
    # print(await db.get_master_and_id())
    await state.update_data({'current_kb': ''})
    await AdminCheckLog.ChoiceRange.set()


async def process_choice_time_callback(call, state):
    full_datetime = call.data.split('_')[1]
    master_username = get_key(await db.get_master_and_id(), str(call.message.chat.id))
    log = await db.get_log_by_full_datetime(full_datetime,
                                            master_username)
    date = [int(d.strip()) for d in log.date.strip('()').split(',')]
    # День, месяц, год
    date_to = datetime.date(date[0], date[1], date[2])
    data = await state.get_data()
    if data.get('current_kb') == 'month':
        default_kb = admin_default_cancel_2_back_check_log_month
    elif data.get('current_kb') == 'week':
        default_kb = admin_default_cancel_2_back_check_log_week
    else:
        default_kb = admin_default_cancel_back_check_log
    await call.message.answer(
        f'''
Время - {log.time}\n
Дата -  {date[2]} / {date[1]} / {date[0]}\n
Мастер - {log.name_master}\n
Клиент - {log.name_client}\n
Услуга - {log.service}''', reply_markup=default_kb)
    kb = InlineKeyboardMarkup()
    # написать callback
    kb.add(InlineKeyboardButton(f'Вернуться к записям на {date[2]} число',
                                callback_data=f'back:to:time_{date_to}_{master_username}'))
    # kb.add(InlineKeyboardButton('Отмена просмотра', callback_data='cancel_check'))
    await call.message.answer(f'{log.phone_number}', reply_markup=kb)


# @dp.callback_query_handler(text_contains='del_', state=AdminCheckLog)
# async def delete_log_by_master():
# pass


@dp.callback_query_handler(text_contains='back:to:time_', state=AdminCheckLog)
async def back_to_date_timetable(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    data = await state.get_data()
    date = [int(i) for i in call.data.split('_')[1].split('-')]
    res = datetime.date(date[0], date[1], date[2])
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id - 1)
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    await process_choice_day(call, res, kb=data.get('current_kb'))
    await AdminCheckLog.ChoiceRange.set()


@dp.callback_query_handler(text_contains='admin:datetime_', chat_id=masters_id,
                           state=AdminCheckLog)
async def process_choice_time(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id - 1)
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    await process_choice_time_callback(call, state)


async def process_choice_day(call, date_time, kb=None):
    current_date = date_time
    year, month, day = current_date.year, current_date.month, current_date.day
    c = calendar.TextCalendar(calendar.MONDAY)
    datetime_with_weekdays = [date for date in c.itermonthdays4(year, month) if date[2] == day][0]
    # today_datetime_log = await db.get_datetime()
    # print(get_key(await db.get_master_and_id(), str(call.message.chat.id)))
    all_today_logs = await db.get_logs_only_date(f'{datetime_with_weekdays}',
                                                 get_key(await db.get_master_and_id(), str(call.message.chat.id)))
    # result_message_list = []
    if all_today_logs:
        kb_time = InlineKeyboardMarkup(row_width=5)
        for log in all_today_logs:
            kb_time.insert(InlineKeyboardButton(f'{log.time}',
                                                callback_data=f'admin:datetime_{datetime_with_weekdays} {log.time}'))
        if kb == 'month':
            await call.message.answer(f'День: {day}', reply_markup=admin_default_cancel_2_back_check_log_month)
        elif kb == 'week':
            await call.message.answer(f'День: {day}', reply_markup=admin_default_cancel_2_back_check_log_week)
        else:
            await call.message.answer(f'День: {day}', reply_markup=admin_default_cancel_back_check_log)
        # await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id-1)
        await call.message.answer(f'\nВыберите время записи, чтобы просмотреть кто записался.',
                                  reply_markup=kb_time)
    else:
        await call.message.answer('Записи клиентов.', reply_markup=admin_default_cancel_check_log)
        await call.message.answer('Никто не записывался на этот день.', reply_markup=check_logs_choice_range)

    # for num, log in enumerate(all_today_logs, 1):
    #     result_message_list.append(f'\n{log}. {log.time} - {log.name_client} - {log.service} - {log.phone_number}')
    #     result_message_list.append('\n')
    # await call.message.answer(all_today_logs)


async def process_choice_week(state, call=None, message=None):
    # await state.update_data('kb': None)
    # data = await state.get_data()
    response = call.message if call else message
    current_date = datetime.datetime.now()
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
        kb_week.insert(InlineKeyboardButton(days.get(week_day), callback_data=days.get(week_day)))
    for day in current_week_days:
        if day < current_date.day or day in current_week_days[5:]:
            kb_week.insert(InlineKeyboardButton(' ', callback_data=f'wrong_date'))
            continue
        kb_week.insert(
            InlineKeyboardButton(day,
                                 callback_data=f'date_{current_date.year}, {current_date.month}, {day}'))
    # kb_week.add(InlineKeyboardButton('Отмена просмотра', callback_data='cancel_check'))
    await state.update_data({'kb': kb_week})
    await response.answer('Записи на неделю', reply_markup=admin_default_cancel_back_check_log)
    await response.answer('Выберите дату записи, '
                          'чтобы просмотреть кто записался на текущей неделе.',
                          reply_markup=kb_week)


@dp.callback_query_handler(state=AdminCheckLog.CheckWeek, text_contains='date_')
async def process_choice_day_of_week(call: CallbackQuery):
    await call.answer(cache_time=60)
    # print(call.data.split('_')[1])
    date = [int(i) for i in call.data.split('_')[1].split(',')]
    # print(date)
    choice_day = datetime.date(date[0], date[1], date[2])
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id - 1)
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    await process_choice_day(call=call, date_time=choice_day, kb='week')
    await AdminCheckLog.ChoiceRange.set()


@dp.callback_query_handler(state=AdminCheckLog.CheckMonths, text_contains='date_')
async def process_choice_day_of_month(call: CallbackQuery):
    await call.answer(cache_time=60)
    # print(call.data.split('_')[1])
    date = [int(i.strip('()')) for i in call.data.split('_')[1].split(',')]
    # print(date)
    choice_day = datetime.date(date[0], date[1], date[2])
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id - 1)
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    await process_choice_day(call=call, date_time=choice_day, kb='month')
    await AdminCheckLog.ChoiceRange.set()


@dp.callback_query_handler(state=AdminCheckLog.ChoiceRange, chat_id=masters_id, text_contains='logs_')
async def choice_range_log(call: CallbackQuery, state: FSMContext):
    result = call.data.split('_')[1]
    await call.answer(cache_time=60)
    current_date = datetime.date.today()
    if result == 'today':
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id - 1)
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        await AdminCheckLog.CheckToday.set()
        await process_choice_day(call, current_date)
        await AdminCheckLog.ChoiceRange.set()
    elif result == 'week':
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id - 1)
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        await AdminCheckLog.CheckWeek.set()
        await process_choice_week(call=call, state=state)
        await state.update_data({'current_kb': 'week'})
    elif result == 'months':
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id - 1)
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        await AdminCheckLog.CheckMonths.set()
        await state.update_data(
            {'current_choice_month': '',
             'current_choice_year': ''})
        await call.message.answer('Записи по месяцам', reply_markup=admin_default_cancel_back_check_log)
        await date_process_enter(call=call, state=state,
                                 year=current_date.year,
                                 month=current_date.month,
                                 day=current_date.day,
                                 service=False)
        await state.update_data({'current_kb': 'month'})
