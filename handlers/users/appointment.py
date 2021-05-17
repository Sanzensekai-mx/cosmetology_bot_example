import logging
import datetime
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, ReplyKeyboardRemove, InlineKeyboardMarkup, \
    InlineKeyboardButton, CallbackQuery, ContentType

from keyboards.default import main_menu_client, phone_number, default_cancel_appointment, \
    default_cancel_appointment_confirm
from keyboards.inline import inline_cancel_appointment
from loader import dp
from states.user_states import UserAppointment
from utils.db_api.models import DBCommands

from utils.general_func import return_kb_mes_services, date_process_enter

db = DBCommands()

logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] '
                           u'#%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO)


async def confirm_or_change(data, mes):
    date = [d.strip() for d in data.get("date").strip("()").split(",")]
    await mes.answer(f''' 
Имя клиента - {data.get("name_client")}\n
Услуга - {data.get("service")}\n
Мастер - {data.get("name_master")}\n
Дата - {date[2]} / {date[1]} / {date[0]}\n
Время - {data.get("time")}\n
Номер телефона - {data.get("phone_number")}''', reply_markup=default_cancel_appointment_confirm)
    await UserAppointment.Confirm.set()


@dp.callback_query_handler(state=UserAppointment, text_contains='cancel_appointment')
async def inline_process_cancel_add_service(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    await call.message.answer('Отмена записи.', reply_markup=main_menu_client)
    await state.reset_state()


@dp.message_handler(Text(equals=['Отмена записи']), state=UserAppointment)
async def default_kb_process_cancel_add_service(message: Message, state: FSMContext):
    await message.answer('Отмена записи.', reply_markup=main_menu_client)
    await state.reset_state()


@dp.message_handler(Text(equals=['Запись']))
async def open_appointment_start(message: Message, state: FSMContext):
    logging.info(f'from: {message.chat.full_name}, text: {message.text.upper()}')
    # LOG you!!!!!!!
    await message.answer('Начало записи.', reply_markup=ReplyKeyboardRemove())
    await message.answer('Введите своё фамилию и имя. Например: Петрина Кристина',
                         reply_markup=inline_cancel_appointment)
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


async def return_kb_masters(service):
    appointment_choice_master = InlineKeyboardMarkup()
    all_masters = await db.all_masters()
    for master in all_masters:
        if service in master.master_services:
            appointment_choice_master.add(InlineKeyboardButton(f'{master.master_name}',
                                                               callback_data=f'm_{master.master_name}'))
    return appointment_choice_master


async def service_process_enter(message, state):
    data = await state.get_data()
    # services_mes, services_kb = await return_kb_mes_services(state)
    await message.answer('Выбор услуги\n'
                         f'Ваша Фамилия и Имя: "{data.get("name_client")}". ', reply_markup=default_cancel_appointment)
    await return_kb_mes_services(message, state)


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
            await UserAppointment.Service.set()
            await service_process_enter(message, state)

    else:
        name_client = message.text.strip()
        data['name_client'] = name_client
        await state.update_data(data)
        await confirm_or_change(data, message)


# Обработка выбранной услуги и занесение ее в state data
@dp.callback_query_handler(state=UserAppointment.Service, text_contains='s_')
async def choice_master(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    service_num = call.data.split('_')[1]
    await call.answer(cache_time=60)
    # all_services_names = data.get('current_services_dict')
    all_services_names = data.get('services_by_page')[data.get('page')]
    service = all_services_names[service_num]
    if not data.get('service'):
        # Принятие выбора услуги
        data['service'] = service
        await state.update_data(data)
        # print(await state.get_data())
        await UserAppointment.Master.set()
        # Выбор даты, функция
        # current_date = datetime.date.today()
        # await date_process_enter(call, state,
        #                          year=current_date.year,
        #                          month=current_date.month,
        #                          day=current_date.day)
        await call.message.answer('Выбор мастера', reply_markup=default_cancel_appointment)
        await call.message.answer(f'Ваша Фамилия и Имя: "{data.get("name_client")}". ' \
                                  f'\nВыбрана услуга: "{data.get("service")}"'
                                  f'\nТеперь выберите мастера из списка ниже.',
                                  reply_markup=await return_kb_masters(service=data.get("service")))
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
        await UserAppointment.Date.set()
        # Выбор даты, функция
        current_date = datetime.date.today()
        await call.message.answer('Выбор даты оказания услуги', reply_markup=default_cancel_appointment)
        await date_process_enter(call, state,
                                 year=current_date.year,
                                 month=current_date.month,
                                 day=current_date.day)
    else:
        data['name_master'] = name_master
        await state.update_data(data)
        await confirm_or_change(data, call.message)


@dp.callback_query_handler(state=UserAppointment.Date, text_contains='month_')
async def change_month_process(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await call.answer(cache_time=60)
    current_date = datetime.datetime.now()
    # current_date = datetime.datetime.now(tz_ulyanovsk)
    # ?
    # current_date += datetime.timedelta(hours=4)
    # await call.message.answer(f'{current_date.hour}:{current_date.minute}')
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
        await call.message.answer('Выбор даты оказания услуги', reply_markup=default_cancel_appointment)
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
        await call.message.answer('Выбор даты оказания услуги', reply_markup=default_cancel_appointment)
        await date_process_enter(call, state,
                                 year=choice_year,
                                 month=choice_month,
                                 day=1)


@dp.callback_query_handler(state=UserAppointment.Date, text_contains='wrong_date')
async def wrong_date_process(call: CallbackQuery):
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
    # time_kb.add(InlineKeyboardButton('Отмена записи', callback_data='cancel_appointment'))
    # Формат даты День/месяц/год
    date = [d.strip() for d in data.get("date").strip("()").split(",")]
    await call.message.answer('Выбор времени оказания услуги', reply_markup=default_cancel_appointment)
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
                                      f'\nВремя:  {data.get("time")}', reply_markup=default_cancel_appointment)
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
        await message.answer('Проверьте введенные данные.', reply_markup=default_cancel_appointment)
        await confirm_or_change(data, message)
        # await message.answer('Нажмите кнопку, чтобы записаться', reply_markup=cancel_appointment_or_confirm)
    else:
        data['phone_number'] = number
        await state.update_data(data)
        await confirm_or_change(data, message)


# @dp.callback_query_handler(text_contains='change', state=UserAppointment.Confirm)
# async def change_some_data(call: CallbackQuery, state: FSMContext):
#     await call.answer(cache_time=60)
#     what_to_change = call.data.split(':')[1]
#     if what_to_change == 'name_client':
#         await call.message.answer('Введите новое имя клиента.')
#         await UserAppointment.Name.set()
#     elif what_to_change == 'name_master':
#         await call.message.answer('Выберите другого мастера.', reply_markup=await return_kb_masters())
#         await UserAppointment.Master.set()
#     elif what_to_change == 'service':
#         res_mes_and_kb = await return_kb_mes_services(state)
#         await call.message.answer(f'Выберите другую услугу. \n{res_mes_and_kb[0]}',
#                                   reply_markup=res_mes_and_kb[1])
#
#         await UserAppointment.Service.set()
#     elif what_to_change == 'date':
#         await call.message.answer('Выберите другую дату.')
#         await UserAppointment.Date.set()
#     elif what_to_change == 'time':
#         await call.message.answer('Выберите другое время.')
#         await UserAppointment.Time.set()


# @dp.callback_query_handler(text_contains='confirm_appointment', state=UserAppointment.Confirm)
# async def confirm_to_db(call: CallbackQuery, state: FSMContext):
@dp.message_handler(Text(equals=['Подтвердить']), state=UserAppointment.Confirm)
async def confirm_to_db(message: Message, state: FSMContext):
    # await call.answer(cache_time=60)
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
    await message.answer('Вы записаны. Нажмите на кнопку \"Мои записи\", чтобы увидеть подробности записи',
                         reply_markup=main_menu_client)  # Исправить reply_markup
    # Тест отправки
    # pic = await db.show_service_test()
    # await bot.send_photo(chat_id=591763264, photo=pic.pic_file_id)
    await state.finish()
