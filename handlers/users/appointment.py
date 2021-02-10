import logging
import datetime
import calendar
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from keyboards.default import main_menu_no_orders
from keyboards.inline import cancel_appointment
from loader import dp
from states.user_states import UserAppointment
from utils.db_api.models import DBCommands
from data.config import admins, masters_and_id

db = DBCommands()

logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] '
                           u'#%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO)


async def confirm_or_change(data, mes):
    kb_confirm = InlineKeyboardMarkup(row_width=4)
    for key in data.keys():
        if key == 'is_this_log_5_in_db':
            break
        change_button = InlineKeyboardButton(f'Изменить {key}', callback_data=f'change:{key}')
        kb_confirm.add(change_button)
    kb_confirm.add(InlineKeyboardButton('Подтвердить', callback_data='сonfirm'))
    await mes.answer(f''' 
Проверьте введенные данные.\n
Название - {data.get("name")}\n
Ссылка на картинку - {data.get("pic_href")}\n
Описание - {data.get("describe")}\n
Ссылка - {data.get("meme_href")}\n''', reply_markup=kb_confirm)
    await UserAppointment.Confirm.set()


@dp.callback_query_handler(chat_id=admins, state=UserAppointment, text_contains='cancel_appointment')
async def process_cancel_add_service(call: CallbackQuery, state: FSMContext):
    logging.info(f'from: {call.message.chat.full_name}, text: {call.message.text}, info: Отмена записи.')
    await call.message.answer('Отмена записи.', reply_markup=main_menu_no_orders)  # Добавить reply_markup
    await state.reset_state()


@dp.message_handler(Text(equals=['Запись']))
async def open_appointment_start(message: Message, state: FSMContext):
    logging.info(f'from: {message.chat.first_name}, text: {message.text}')
    # LOG you!!!!!!!
    await message.answer('Введите своё фамилию и имя. Например: Петрина Кристина',
                         reply_markup=cancel_appointment)
    await UserAppointment.Name.set()
    await state.update_data(
        {'name_client': '',
         'name_master': '',
         'service': '',
         'user_id': '',
         'date': '',
         'time': '',
         'phone_number': '',
         'is_this_log_5_in_db': ''
         }
    )


@dp.message_handler(state=UserAppointment.Name)
async def open_appointment_enter_name(message: Message, state: FSMContext):
    data = await state.get_data()
    if not data.get('name_client'):
        # Принятие ввода имени клиента
        name_client = message.text.strip()
        data['name_client'] = name_client
        data['user_id'] = message.chat.id
        data['is_this_log_5_in_db'] = '5 записей с вашего аккаунта уже существует в БД. Больше нельзя.' \
            if await db.is_this_log_5_in_db(name_client) \
            else 'Запись возможна.'
        is_this_log_5_in_db = data.get('is_this_log_5_in_db')
        # Если существует 5 записей с одного chat_id, то выводится предупреждение и состояние сбрасывается
        if is_this_log_5_in_db is True:
            await message.answer(f'{is_this_log_5_in_db}')
            await state.finish()
        await state.update_data(data)
        await UserAppointment.Master.set()
        cancel_appointment_choice_master = InlineKeyboardMarkup()
        for master in masters_and_id.keys():
            cancel_appointment_choice_master.add(InlineKeyboardButton(f'{master}',
                                                                      callback_data=f'm_{master}'))
        cancel_appointment_choice_master.add(InlineKeyboardButton('Отмена записи',
                                                                  callback_data='cancel_appointment'))
        await message.answer(f'Ваше Фамилия и Имя: "{data.get("name_client")}". '
                             '\nВыберите мастера:', reply_markup=cancel_appointment_choice_master)

    else:
        name_client = message.text.strip()
        data['name_client'] = name_client
        await state.update_data(data)
        await confirm_or_change(data, message)


# !!!!!!!!! Вывод списка услуг в сообщении? Кнопки с цифрами, иначе все длина
# какой-нибудь услуги может не уместиться в область кнопки
async def service_process_enter(call, state):
    data = await state.get_data()
    cancel_appointment_choice_service = InlineKeyboardMarkup()
    services = await db.all_services()
    for service in services:
        service_name = service.name
        service_price = service.price
        service_time = service.time
        cancel_appointment_choice_service.add(InlineKeyboardButton(f'{service_name} {service_price}',
                                                                   callback_data=f's_{service_name}'))
    cancel_appointment_choice_service.add(InlineKeyboardButton('Отмена записи',
                                                               callback_data='cancel_appointment'))
    await call.message.answer(f'Ваше Фамилия и Имя: "{data.get("name_client")}". '
                              f'\nМастер: "{data.get("name_master")}"'
                              '\nВыберите услугу:', reply_markup=cancel_appointment_choice_service)


# Обработка выбранного мастера и занесение его в state data, запуск функции для выдачи кнопок с услугами
@dp.callback_query_handler(state=UserAppointment.Master, text_contains='m_')
async def choice_master(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    name_master = call.data.split('_')[1]
    await call.answer(cache_time=60)
    if not data.get('name_master'):
        # Принятие выбора мастера
        data['name_master'] = name_master
        await state.update_data(data)
        await UserAppointment.Service.set()
        await service_process_enter(call, state)
    else:
        data['name_master'] = name_master
        await state.update_data(data)
        await confirm_or_change(data, call.message)


# Сделать
async def date_process_enter(call, state):
    data = await state.get_data()
    service = await db.get_service(data.get('service'))
    c = calendar.TextCalendar(calendar.MONDAY)
    current_date = datetime.date.today()
    print_c = c.formatmonth(current_date.year, current_date.month)
    # time_service = service.time
    inline_calendar = InlineKeyboardMarkup(row_width=7)
    # inline_calendar.add(InlineKeyboardButton('<', callback_data='month_previous'))
    inline_calendar.insert(InlineKeyboardButton(f'{print_c.split()[0]} {print_c.split()[1]}', callback_data='month'))
    inline_calendar.insert(InlineKeyboardButton('>', callback_data='month_next'))
    for week_day in [item for item in print_c.split()][2:9]:
        if week_day == 'Mo':
            inline_calendar.add(InlineKeyboardButton(week_day, callback_data=week_day))
            continue
        inline_calendar.insert(InlineKeyboardButton(week_day, callback_data=week_day))
    for day in [date for date in c.itermonthdays(current_date.year, current_date.month)]:
        if day == 0 or current_date.day > day:
            inline_calendar.insert(InlineKeyboardButton(' ', callback_data=f'wrong_date'))
            continue
        inline_calendar.insert(InlineKeyboardButton(day, callback_data=f'date_{day}'))
    inline_calendar.add(InlineKeyboardButton('Отмена записи', callback_data='cancel_appointment'))
    # print(type([date for date in c.itermonthdays(current_date.year, current_date.month)]))
    print(print_c)
    # print(print_c.split())
    # await call.message.answer('Календарь', reply_markup=inline_calendar)
    await call.message.answer(f'Ваше Фамилия и Имя: "{data.get("name_client")}". '
                              f'\nМастер: "{data.get("name_master")}"'
                              f'\nУслуга: "{service.name}"', reply_markup=inline_calendar)


# Обработка выбранной услуги и занесение ее в state data
@dp.callback_query_handler(state=UserAppointment.Service, text_contains='s_')
async def choice_master(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    service = call.data.split('_')[1]
    await call.answer(cache_time=60)
    if not data.get('service'):
        # Принятие выбора услуги
        data['service'] = service
        await state.update_data(data)
        # print(await state.get_data())
        await UserAppointment.Date.set()
        # Выбор даты, функция
        await date_process_enter(call, state)
    else:
        data['service'] = service
        await state.update_data(data)
        await confirm_or_change(data, call.message)


async def time_process_enter(call, state):
    data = await state.get_data()
    await call.message.answer(f'Ваше Фамилия и Имя: "{data.get("name_client")}". '
                              f'\nМастер: "{data.get("name_master")}"'
                              f'\nУслуга: "{data.get("service")}"'
                              f'\nДата: {data.get("date")}')


@dp.callback_query_handler(state=UserAppointment.Date, text_contains='wrong_date')
async def wrong_date_process(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    await call.message.answer('Дата неактуальна, выберите не пустую дату.')
    # await state.finish()


@dp.callback_query_handler(state=UserAppointment.Date, text_contains='date_')
async def choice_date(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    date = call.data.split('_')[1]
    await call.answer(cache_time=60)
    if not data.get('date'):
        # Принятие выбора услуги
        data['date'] = date
        await state.update_data(data)
        # print(await state.get_data())
        await UserAppointment.Time.set()
        # Выбор даты, функция
        await time_process_enter(call, state)
    else:
        data['date'] = date
        await state.update_data(data)
        await confirm_or_change(data, call.message)
