import logging
import datetime
import calendar
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, ReplyKeyboardRemove, InlineKeyboardMarkup, \
    InlineKeyboardButton, CallbackQuery, ContentType

from keyboards.default import main_menu_client, phone_number
from keyboards.inline import cancel_appointment, cancel_appointment_or_confirm
from loader import dp
from states.user_states import UserAppointment
from utils.db_api.models import DBCommands
from data.config import masters_and_id

db = DBCommands()

logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] '
                           u'#%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO)


async def confirm_or_change(data, mes):
    kb_confirm = InlineKeyboardMarkup(row_width=4)
    for_kb_name_items = {'name_client': 'имя клиента', 'name_master': 'мастера',
                         'service': 'услугу', 'date': 'дату', 'time': 'время'}
    for key in data.keys():
        if key in ['is_this_log_5_in_db', 'current_choice_month',
                   'current_choice_year', 'user_id', 'full_datetime',
                   'current_services_dict', 'phone_number']:
            continue
        change_button = InlineKeyboardButton(f'Изменить {for_kb_name_items.get(key)}', callback_data=f'change:{key}')
        kb_confirm.add(change_button)
    kb_confirm.add(InlineKeyboardButton('Подтвердить', callback_data='confirm_appointment'))
    kb_confirm.add(InlineKeyboardButton('Отмена записи', callback_data='cancel_appointment'))
    await mes.answer(f''' 
Имя клиента - {data.get("name_client")}\n
Мастер - {data.get("name_master")}\n
Услуга - {data.get("service")}\n
Дата - {data.get("date")}\n
Время - {data.get("time")}\n
Номер телефона - {data.get("phone_number")}''', reply_markup=kb_confirm)
    await UserAppointment.Confirm.set()


@dp.callback_query_handler(state=UserAppointment, text_contains='cancel_appointment')
async def process_cancel_add_service(call: CallbackQuery, state: FSMContext):
    logging.info(f'from: {call.message.chat.full_name}, text: {call.message.text}, info: Отмена записи.')
    await call.answer(cache_time=60)
    await call.message.answer('Отмена записи.', reply_markup=main_menu_client)  # Добавить reply_markup
    await state.reset_state()


@dp.message_handler(Text(equals=['Запись']))
async def open_appointment_start(message: Message, state: FSMContext):
    logging.info(f'from: {message.chat.first_name}, text: {message.text}')
    # LOG you!!!!!!!
    await message.answer('Начало записи.', reply_markup=ReplyKeyboardRemove())
    await message.answer('Введите своё фамилию и имя. Например: Петрина Кристина',
                         reply_markup=cancel_appointment)
    await UserAppointment.Name.set()
    await state.update_data(
        {'name_client': '',
         'name_master': '',
         'service': '',
         'user_id': '',
         'full_datetime': '',
         'date': '',
         'time': '',
         'phone_number': '',
         'is_this_log_5_in_db': '',
         'current_choice_month': '',
         'current_choice_year': '',
         'current_services_dict': {}
         }
    )


async def return_kb_masters():
    cancel_appointment_choice_master = InlineKeyboardMarkup()
    for master in masters_and_id.keys():
        cancel_appointment_choice_master.add(InlineKeyboardButton(f'{master}',
                                                                  callback_data=f'm_{master}'))
    cancel_appointment_choice_master.add(InlineKeyboardButton('Отмена записи',
                                                              callback_data='cancel_appointment'))
    return cancel_appointment_choice_master


@dp.message_handler(state=UserAppointment.Name)
async def open_appointment_enter_name(message: Message, state: FSMContext):
    data = await state.get_data()
    if not data.get('name_client'):
        # Принятие ввода имени клиента
        name_client = message.text.strip()
        data['name_client'] = name_client
        data['user_id'] = message.chat.id
        data['is_this_log_5_in_db'] = await db.is_this_log_5_in_db(message.chat.id)
        await state.update_data(data)
        is_this_log_5_in_db = data.get('is_this_log_5_in_db')
        # Если существует 5 записей с одного chat_id, то выводится предупреждение и состояние сбрасывается
        if data.get('is_this_log_5_in_db') is True:
            await message.answer('5 записей с вашего аккаунта уже существует в БД. Больше нельзя.',
                                 reply_markup=main_menu_client)
            await state.finish()
        # await message.answer(is_this_log_5_in_db)
        # await state.update_data(data)
        else:
            await UserAppointment.Master.set()
            # cancel_appointment_choice_master = InlineKeyboardMarkup()
            # for master in masters_and_id.keys():
            #     cancel_appointment_choice_master.add(InlineKeyboardButton(f'{master}',
            #                                                               callback_data=f'm_{master}'))
            # cancel_appointment_choice_master.add(InlineKeyboardButton('Отмена записи',
            #                                                           callback_data='cancel_appointment'))
            await message.answer(f'Ваше Фамилия и Имя: "{data.get("name_client")}". '
                                 '\nВыберите мастера:', reply_markup=await return_kb_masters())

    else:
        name_client = message.text.strip()
        data['name_client'] = name_client
        await state.update_data(data)
        await confirm_or_change(data, message)


# Возвращает список, где 1-ый элемент - сообщение, 2-ой - клавиатура
async def return_kb_mes_services(state):
    data_from_state = await state.get_data()
    cancel_appointment_choice_service = InlineKeyboardMarkup(row_width=5)
    services = await db.all_services()
    res_message = ''
    current_services_dict = {}
    for num, service in enumerate(services, 1):
        service_name = service.name
        service_price = service.price
        res_message += f'\n{num}. {service_name} - {service_price}'
        current_services_dict[str(num)] = service_name
        cancel_appointment_choice_service.insert(InlineKeyboardButton(f'{num}',
                                                                      callback_data=f's_{num}'))
        # cancel_appointment_choice_service.add(InlineKeyboardButton(f'{service_name} {service_price}',
        #                                                            callback_data=f's_{service_name}'))
    cancel_appointment_choice_service.add(InlineKeyboardButton('Отмена записи',
                                                               callback_data='cancel_appointment'))
    data_from_state['current_services_dict'] = current_services_dict
    await state.update_data(data_from_state)
    return [res_message, cancel_appointment_choice_service]


# !!!!!!!!! Вывод списка услуг в сообщении? Кнопки с цифрами, иначе все длина
# какой-нибудь услуги может не уместиться в область кнопки
async def service_process_enter(call, state):
    data = await state.get_data()
    # cancel_appointment_choice_service = InlineKeyboardMarkup()
    # services = await db.all_services()
    # for service in services:
    #     service_name = service.name
    #     service_price = service.price
    #     service_time = service.time
    #     cancel_appointment_choice_service.add(InlineKeyboardButton(f'{service_name} {service_price}',
    #                                                                callback_data=f's_{service_name}'))
    # cancel_appointment_choice_service.add(InlineKeyboardButton('Отмена записи',
    #                                                            callback_data='cancel_appointment'))
    res_mes_and_kb = await return_kb_mes_services(state)
    await call.message.answer(f'Ваше Фамилия и Имя: "{data.get("name_client")}". ' \
                              f'\nМастер: "{data.get("name_master")}" ' \
                              f'\nВыберите услугу:\n{res_mes_and_kb[0]}',
                              reply_markup=res_mes_and_kb[1])


# Обработка выбранной услуги и занесение ее в state data
@dp.callback_query_handler(state=UserAppointment.Service, text_contains='s_')
async def choice_master(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    service_num = call.data.split('_')[1]
    await call.answer(cache_time=60)
    all_services_names = data.get('current_services_dict')
    service = all_services_names[service_num]
    if not data.get('service'):
        # Принятие выбора услуги
        data['service'] = service
        await state.update_data(data)
        # print(await state.get_data())
        await UserAppointment.Date.set()
        # Выбор даты, функция
        current_date = datetime.date.today()
        await date_process_enter(call, state,
                                 year=current_date.year,
                                 month=current_date.month,
                                 day=current_date.day)
    else:
        data['service'] = service
        await state.update_data(data)
        await confirm_or_change(data, call.message)


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


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! Сделать, сзязь с БД, новая таблица в БД datetime?
async def date_process_enter(call, state, year, month, day):
    data = await state.get_data()
    c = calendar.LocaleTextCalendar(calendar.MONDAY, locale='Russian_Russia')
    service = await db.get_service(data.get('service'))
    current_date = datetime.date.today()
    if month == current_date.month and year == current_date.year:
        month = current_date.month
        year = current_date.year
        day = current_date.day
    # print(c.formatyear(current_date.year))
    print_c = c.formatmonth(year, month)
    # time_service = service.time
    inline_calendar = InlineKeyboardMarkup(row_width=7)
    if (month != current_date.month and year == current_date.year) \
            or ((month != current_date.month or month == current_date.month)
                and year != current_date.year):
        inline_calendar.add(InlineKeyboardButton('<', callback_data='month_previous'))
    data['current_choice_month'] = month
    data['current_choice_year'] = year
    await state.update_data(data)
    inline_calendar.insert(InlineKeyboardButton(f'{print_c.split()[0]} {print_c.split()[1]}', callback_data=' '))
    inline_calendar.insert(InlineKeyboardButton('>', callback_data='month_next'))
    for week_day in [item for item in print_c.split()][2:9]:
        if week_day == 'Пн':
            inline_calendar.add(InlineKeyboardButton(week_day, callback_data=week_day))
            continue
        inline_calendar.insert(InlineKeyboardButton(week_day, callback_data=week_day))
    for day_cal in [date for date in c.itermonthdays4(year, month)]:
        # Исключает дни другого месяца, прошедшие дни и выходные дни (Суббота, Воскресенье)
        if day_cal[2] == 0 \
                or day > day_cal[2] \
                or day_cal[2] in [date[0] for date
                                  in c.itermonthdays2(year, month)
                                  if date[1] in [5, 6]] \
                or day_cal[1] != month:
            inline_calendar.insert(InlineKeyboardButton(' ', callback_data=f'wrong_date'))
            continue
        inline_calendar.insert(InlineKeyboardButton(day_cal[2], callback_data=f'date_{day_cal}'))
    inline_calendar.add(InlineKeyboardButton('Отмена записи', callback_data='cancel_appointment'))
    # print([date[0] for date in c.itermonthdays2(current_date.year, current_date.month) if date[1] in [5, 6]])
    # print([date for date in c.itermonthdays(current_date.year, current_date.month)])
    # print([date for date in c.itermonthdays2(current_date.year, current_date.month)])
    # print([date for date in c.itermonthdays3(current_date.year, current_date.month)])
    # print([date for date in c.itermonthdays4(year, month)])
    # print(print_c)
    # print(print_c.split())
    await call.message.answer(f'Ваше Фамилия и Имя: "{data.get("name_client")}". '
                              f'\nМастер: "{data.get("name_master")}"'
                              f'\nУслуга: "{service.name}"', reply_markup=inline_calendar)


@dp.callback_query_handler(state=UserAppointment.Date, text_contains='month_')
async def change_month_process(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await call.answer(cache_time=60)
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
        await date_process_enter(call, state,
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
        await date_process_enter(call, state,
                                 year=choice_year,
                                 month=choice_month,
                                 day=1)


@dp.callback_query_handler(state=UserAppointment.Date, text_contains='wrong_date')
async def wrong_date_process(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    await call.message.answer('Дата неактуальна, выберите не пустую дату.')


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
        await db.add_log_datetime(data.get('date'), data.get('name_master'))
        await UserAppointment.Time.set()
        # Выбор даты, функция
        await time_process_enter(call, state)
    else:
        data['date'] = date
        await state.update_data(data)
        await confirm_or_change(data, call.message)


async def time_process_enter(call, state):
    data = await state.get_data()
    time_dict = await db.get_dict_of_time(data.get('date'), data.get('name_master'))
    time_kb = InlineKeyboardMarkup(row_width=5)
    for time, val in time_dict.items():
        if val is False:
            if time == '10:00':
                time_kb.add(InlineKeyboardButton(f'{time}', callback_data=f'time_{time}'))
            else:
                time_kb.insert(InlineKeyboardButton(f'{time}', callback_data=f'time_{time}'))
    time_kb.add(InlineKeyboardButton('Отмена записи', callback_data='cancel_appointment'))
    # Формат даты День/месяц/год
    date = [d.strip() for d in data.get("date").strip("()").split(",")]
    await call.message.answer(f'Ваше Фамилия и Имя: "{data.get("name_client")}". '
                              f'\nМастер: "{data.get("name_master")}"'
                              f'\nУслуга: "{data.get("service")}"'
                              f'\nДата:  {date[2]} / {date[1]} / {date[0]}', reply_markup=time_kb)  # reply_markup


@dp.callback_query_handler(state=UserAppointment.Time, text_contains='time_')
async def choice_date(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    time = call.data.split('_')[1]
    await call.answer(cache_time=60)
    if not data.get('time'):
        # Принятие выбора услуги
        data['time'] = time
        data['full_datetime'] = f'{data.get("date")} {data.get("time")}'
        await state.update_data(data)
        if await db.is_client_full_datetime_in_db(data.get('full_datetime'), data.get('name_client')):
            await call.message.answer('Вы уже записаны на это время у другого мастера',
                                      reply_markup=main_menu_client)
            await state.finish()
        # print(await state.get_data())
        else:
            await UserAppointment.PhoneNumber.set()
            date = [d.strip() for d in data.get("date").strip("()").split(",")]
            await call.message.answer(f'Ваше Фамилия и Имя: "{data.get("name_client")}". '
                                      f'\nМастер: "{data.get("name_master")}"'
                                      f'\nУслуга: "{data.get("service")}"'
                                      f'\nДата:  {date[2]} / {date[1]} / {date[0]}'
                                      f'\nВремя:  {data.get("time")}', reply_markup=cancel_appointment)
            await call.message.answer('Нажмите на кнопку ниже, чтобы отправить номер телефона.',
                                      reply_markup=phone_number)
        # Выбор даты, функция
        # await time_process_enter(call, state)
    else:
        data['time'] = time
        await state.update_data(data)
        await confirm_or_change(data, call.message)


@dp.message_handler(content_types=ContentType.CONTACT,
                    state=UserAppointment.PhoneNumber)
async def choice_date(message: Message, state: FSMContext):
    data = await state.get_data()
    number = message.contact.phone_number
    # time = call.data.split('_')[1]
    # await call.answer(cache_time=60)
    if not data.get('phone_number'):
        # Принятие выбора услуги
        data['phone_number'] = number
        await state.update_data(data)
        # print(await state.get_data())
        await UserAppointment.Confirm.set()
        await message.answer('Проверьте введенные данные.', reply_markup=ReplyKeyboardRemove())
        await confirm_or_change(data, message)
        # await message.answer('Нажмите кнопку, чтобы записаться', reply_markup=cancel_appointment_or_confirm)
    else:
        data['phone_number'] = number
        await state.update_data(data)
        await confirm_or_change(data, message)


@dp.callback_query_handler(text_contains='change', state=UserAppointment.Confirm)
async def change_some_data(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    what_to_change = call.data.split(':')[1]
    if what_to_change == 'name_client':
        await call.message.answer('Введите новое имя клиента.')
        await UserAppointment.Name.set()
    elif what_to_change == 'name_master':
        await call.message.answer('Выберите другого мастера.', reply_markup=await return_kb_masters())
        await UserAppointment.Master.set()
    elif what_to_change == 'service':
        res_mes_and_kb = await return_kb_mes_services(state)
        await call.message.answer(f'Выберите другую услугу. \n{res_mes_and_kb[0]}',
                                  reply_markup=res_mes_and_kb[1])

        await UserAppointment.Service.set()
    elif what_to_change == 'date':
        await call.message.answer('Выберите другую дату.')
        await UserAppointment.Date.set()
    elif what_to_change == 'time':
        await call.message.answer('Выберите другое время.')
        await UserAppointment.Time.set()


@dp.callback_query_handler(text_contains='confirm_appointment', state=UserAppointment.Confirm)
async def confirm_to_db(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await db.add_update_date(datetime_one=data.get('date'),
                             time=data.get('time'), master=data.get('name_master'))
    await db.add_log(
        user_id=data.get('user_id'),
        name_client=data.get('name_client'),
        name_master=data.get('name_master'),
        service=data.get('service'),
        full_datetime=data.get('full_datetime'),
        date=data.get('date'),
        time=data.get('time'),
        phone_number=data.get('phone_number'))
    await call.message.answer('Вы записаны. Нажмите на кнопку \"Мои записи\", чтобы увидеть подробности записи',
                              reply_markup=main_menu_client)  # Исправить reply_markup
    # Тест отправки
    # pic = await db.show_service_test()
    # await bot.send_photo(chat_id=591763264, photo=pic.pic_file_id)
    await state.finish()
