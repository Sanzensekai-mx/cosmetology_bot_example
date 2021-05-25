import logging
import datetime
import calendar
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, ReplyKeyboardRemove, InlineKeyboardMarkup, \
    InlineKeyboardButton, CallbackQuery
from loader import dp, bot
from utils.db_api.models import DBCommands
from states.admin_states import AdminDelLog
from keyboards.default import main_menu_admin, admin_default_cancel_del_log, admin_default_cancel_back_del_log
from data.config import admins, masters_id
from utils.general_func import date_process_enter
from utils.general_func import get_key

db = DBCommands()


@dp.message_handler(Text(equals=['Закрыть меню удаления записей']), state=AdminDelLog, chat_id=admins)
async def default_process_cancel_check_logs(message: Message, state: FSMContext):
    await message.answer('Отмена просмотра записей для удаления', reply_markup=main_menu_admin)
    await state.reset_state()


@dp.message_handler(Text(equals=['Удаление записи']), chat_id=admins)
async def start_del_log(message: Message, state: FSMContext):
    logging.info(f'from: {message.chat.full_name}, text: {message.text.upper()}')
    kb_masters = InlineKeyboardMarkup()
    all_masters = await db.all_masters()
    for master in all_masters:
        kb_masters.add(InlineKeyboardButton(text=master.master_name,
                                            callback_data=f'm_{master.master_name}'))
    await message.answer('Выбор мастера.', reply_markup=admin_default_cancel_del_log)
    await message.answer('Выберите мастера для удаления записей к ним', reply_markup=kb_masters)
    await AdminDelLog.ChoiceMaster.set()
    await state.update_data(
        {'name_master': '',
         'full_datetime': '',
         }
    )


@dp.callback_query_handler(text_contains='m_', chat_id=admins, state=AdminDelLog.ChoiceMaster)
async def process_choice_master_date_del_log(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    data = await state.get_data()
    choice_master = call.data.split('_')[1]
    data['name_master'] = choice_master
    await state.update_data(data)
    # await AdminCheckLog.CheckMonths.set()
    await AdminDelLog.ChoiceDate.set()
    current_date = datetime.date.today()
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id - 1)
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    await call.message.answer('Записи по месяцам', reply_markup=admin_default_cancel_del_log)
    await date_process_enter(call=call, state=state,
                             year=current_date.year,
                             month=current_date.month,
                             day=current_date.day)
    # data = await state.get_data()
    # print(data.get('current_choice_month'))
    # print(data.get('current_choice_year'))


async def process_choice_day(call, date_time, state):
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
        # kb_time.add(InlineKeyboardButton('Назад к выбору даты', callback_data='back_months'))
        await call.message.answer(f'День: {day} ', reply_markup=admin_default_cancel_del_log)
        await call.message.answer(f'\nВыберите время записи, чтобы просмотреть кто записался.',
                                  reply_markup=kb_time)
    else:
        await call.message.answer('Записи клиентов.', reply_markup=admin_default_cancel_del_log)
        await call.message.answer('Никто не записывался на этот день.')
        await AdminDelLog.ChoiceDate.set()
        await date_process_enter(call=call, state=state,
                                 year=current_date.year,
                                 month=current_date.month,
                                 day=current_date.day)


@dp.callback_query_handler(state=AdminDelLog.ChoiceDate, text_contains='date_')
async def process_choice_day_of_month(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    # print(call.data.split('_')[1])
    date = [int(i.strip('()')) for i in call.data.split('_')[1].split(',')]
    # print(date)
    choice_day = datetime.date(date[0], date[1], date[2])
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id - 1)
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    await AdminDelLog.ChoiceTime.set()
    await process_choice_day(call=call, date_time=choice_day, state=state)


@dp.callback_query_handler(text_contains='admin:datetime_', chat_id=masters_id,
                           state=AdminDelLog.ChoiceTime)
async def process_choice_time(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id - 1)
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    full_datetime = call.data.split('_')[1]
    # master_username = get_key(await db.get_master_and_id(), str(call.message.chat.id))
    data = await state.get_data()
    master_username = data.get('name_master')
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
Услуга - {log.service}''', reply_markup=admin_default_cancel_del_log)
    kb = InlineKeyboardMarkup()
    # написать callback
    # kb.add(InlineKeyboardButton(f'Удалить запись эту запись', callback_data=f'del_{full_datetime}_{master_username}'))
    # kb.add(InlineKeyboardButton(f'Вернуться к записям на {date[2]} число',
    #                             callback_data=f'back:to:time_{date_to}_{master_username}'))
    kb.add(InlineKeyboardButton(f'Удалить запись', callback_data=f'del_{full_datetime}_{master_username}'))
    # kb.add(InlineKeyboardButton('Отмена просмотра', callback_data='cancel_check'))
    await call.message.answer(f'{log.phone_number}', reply_markup=kb)


@dp.callback_query_handler(chat_id=admins, state=AdminDelLog.ChoiceTime, text_contains='del_')
async def process_del_log(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    callback_data = call.data.split('_')
    full_datetime, master_username = callback_data[1], callback_data[2]
    datetime_one = await db.get_log_by_full_datetime(full_datetime, master_username)
    # datetime_obj = await db.get_datetime(datetime_one, master_username)
    await db.del_log(full_datetime, master_username)
    choice_time = full_datetime.split()[-1]
    # await db.del_datetime(datetime_one, master_username)
    await db.add_update_date(datetime_one=datetime_one.date, time=choice_time, master=master_username)
    await call.message.answer('Запись удалена', reply_markup=main_menu_admin)
    await state.reset_state()
