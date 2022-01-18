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
from keyboards.default import main_menu_admin, admin_default_cancel_del_log
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
    await call.message.answer('Записи по месяцам')
    await date_process_enter(call=call, state=state,
                             year=current_date.year,
                             month=current_date.month,
                             day=current_date.day)
    # data = await state.get_data()
    # print(data.get('current_choice_month'))
    # print(data.get('current_choice_year'))


async def process_choice_day(call, date):
    current_date = date
    c = calendar.TextCalendar(calendar.MONDAY)
    datetime_with_weekdays = \
        [d for d in c.itermonthdates(current_date.year, current_date.month) if d.day == current_date.day][0]
    # today_datetime_log = await db.get_datetime()
    print(get_key(await db.get_master_and_id(), str(call.message.chat.id)))
    all_today_recs = await db.get_recs_only_date(datetime_with_weekdays,
                                                 get_key(await db.get_master_and_id(), str(call.message.chat.id)))
    # result_message_list = []

    if all_today_recs:
        kb_time = InlineKeyboardMarkup(row_width=5)
        for rec in all_today_recs:
            datetime_stamp = datetime.datetime.timestamp(datetime.datetime.combine(datetime_with_weekdays, rec.time))
            kb_time.insert(InlineKeyboardButton(f'{rec.time.strftime("%H:%M")}',
                                                callback_data=f'admin:datetime_{int(datetime_stamp)}'))
        kb_time.add(InlineKeyboardButton('Назад к выбору даты', callback_data='back_months'))
        await call.message.answer(f'День: {current_date.day} '
                                  f'\nВыберите время записи, чтобы просмотреть кто записался.',
                                  reply_markup=kb_time)
        await AdminDelLog.ChoiceTime.set()
    else:
        await call.message.answer('Записи клиентов.')
        await call.message.answer('Никто не записывался на этот день.')
        await AdminDelLog.ChoiceDate.set()


@dp.callback_query_handler(state=AdminDelLog.ChoiceDate, text_contains='date_')
async def process_choice_day_of_month(call: CallbackQuery):
    await call.answer(cache_time=60)
    # print(call.data.split('_')[1])
    date = call.data.split('_')[1]
    # print(date)
    choice_day = datetime.datetime.fromtimestamp(int(date))
    await process_choice_day(call=call, date=choice_day)


@dp.callback_query_handler(text_contains='admin:datetime_', chat_id=masters_id,
                           state=AdminDelLog.ChoiceTime)
async def process_choice_time(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    full_datetime = int(call.data.split('_')[1])
    # master_username = get_key(await db.get_master_and_id(), str(call.message.chat.id))
    data = await state.get_data()
    master_username = data.get('name_master')
    datetime_obj = datetime.datetime.fromtimestamp(full_datetime)
    rec = await db.get_rec_by_full_datetime(datetime_obj,
                                            master_username)
    date = rec.date
    # День, месяц, год
    date_to = datetime_obj.date()
    await call.message.answer(
        f'''
Время - {rec.time}\n
Дата -  {date.day}.{str(date.month).ljust(2, '0')}.{date.year}\n
Мастер - {rec.name_master}\n
Клиент - {rec.name_client}\n
Услуга - {rec.service}''')
    kb = InlineKeyboardMarkup()
    # написать callback
    # kb.add(InlineKeyboardButton(f'Удалить запись эту запись', callback_data=f'del_{full_datetime}_{master_username}'))
    kb.add(InlineKeyboardButton(f'Вернуться к записям на {date.day} число',
                                callback_data=f'back:to:time_{full_datetime}_{master_username}'))
    kb.add(InlineKeyboardButton(f'Удалить запись', callback_data=f'del_{full_datetime}_{master_username}'))
    # kb.add(InlineKeyboardButton('Отмена просмотра', callback_data='cancel_check'))
    await call.message.answer(f'{rec.phone_number}', reply_markup=kb)


@dp.callback_query_handler(chat_id=admins, state=AdminDelLog.ChoiceTime, text_contains='del_')
async def process_del_rec(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    callback_data = call.data.split('_')
    full_datetime, master_username = callback_data[1], callback_data[2]
    datetime_obj = datetime.datetime.fromtimestamp(int(full_datetime))
    datetime_one = await db.get_rec_by_full_datetime(datetime_obj, master_username)
    rec_obj = await db.get_rec_by_full_datetime(datetime_obj, master_username)
    master_obj = await db.get_master(master_username)
    await db.del_rec(datetime_obj, master_username)
    choice_time = datetime_obj.time()
    # await db.del_datetime(datetime_one, master_username)
    await db.add_update_date(date=datetime_one.date, time=choice_time, master=master_username)
    await call.message.answer('Запись удалена', reply_markup=main_menu_admin)
    # отбивка пользователю об удалении его записи
    await bot.send_message(chat_id=rec_obj.user_id, text=f'Ваша запись:\n'
                                                         f'Дата: {datetime_obj.day}.{str(datetime_obj.month).ljust(2, "0")}.{datetime_obj.year}\n'
                                                         f'Время: {choice_time}\n'
                                                         f'Была удалена.')
    # отбивка мастера об удалении записи к нему
    await bot.send_message(chat_id=master_obj.master_user_id, text=f'Запись к вам:\n'
                                                               f'Дата: {datetime_obj.day}.{str(datetime_obj.month).ljust(2, "0")}.{datetime_obj.year}\n'
                                                               f'Время: {choice_time}\n'
                                                               f'Клиент: {rec_obj.name_client}\n'
                                                               f'Была удалена администратором.')
    await state.reset_state()


@dp.callback_query_handler(text_contains='back:to:time_', state=AdminDelLog)
async def back_to_date_timetable(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    data = await state.get_data()
    date = datetime.datetime.fromtimestamp(int(call.data.split('_')[1])).date()
    # await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id - 1)
    # await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    await process_choice_day(call, date)
    await AdminDelLog.ChoiceTime.set()


@dp.callback_query_handler(text_contains='back_months', state=AdminDelLog)
async def process_back_to_calendar(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    # current_date = datetime.datetime.now()
    # await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 2)
    # await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    data = await state.get_data()
    await date_process_enter(call=call,
                             state=state,
                             year=data.get('current_choice_year'),
                             month=data.get('current_choice_month'),
                             day=1, service=False)
    await AdminDelLog.ChoiceDate.set()
