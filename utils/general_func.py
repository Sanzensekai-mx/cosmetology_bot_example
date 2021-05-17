import calendar
import datetime
from aiogram.types import Message, ReplyKeyboardRemove, InlineKeyboardMarkup, \
    InlineKeyboardButton
from utils.db_api.models import DBCommands
from data.config import days, months

db = DBCommands()


# 1-ый элемент - сообщение, 2-ой - клавиатура
async def return_kb_mes_services(state):
    data_from_state = await state.get_data()
    choice_service_kb = InlineKeyboardMarkup(row_width=5)
    services = await db.all_services()
    res_message = ''
    current_services_dict = {}
    for num, service in enumerate(services, 1):
        res_message += f'\n{num}. {service.name} - {service.price}'
        current_services_dict[str(num)] = service.name
        choice_service_kb.insert(InlineKeyboardButton(f'{num}',
                                                      callback_data=f's_{num}'))
    data_from_state['current_services_dict'] = current_services_dict
    await state.update_data(data_from_state)
    return res_message, choice_service_kb


async def date_process_enter(call, state, year, month, day, service=True):
    data = await state.get_data()
    c = calendar.TextCalendar(calendar.MONDAY)
    if service:
        service = await db.get_service(data.get('service'))
    # current_date = datetime.datetime.now(tz_ulyanovsk)
    current_date = datetime.datetime.now()
    # ?
    # current_date += datetime.timedelta(hours=4)
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
    inline_calendar.insert(InlineKeyboardButton(f'{months.get(print_c.split()[0])} {print_c.split()[1]}',
                                                callback_data=' '))
    inline_calendar.insert(InlineKeyboardButton('>', callback_data='month_next'))
    for week_day in [item for item in print_c.split()][2:9]:
        if week_day == 'Mo':
            inline_calendar.add(InlineKeyboardButton(days.get(week_day), callback_data=days.get(week_day)))
            continue
        inline_calendar.insert(InlineKeyboardButton(days.get(week_day), callback_data=days.get(week_day)))
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
    # inline_calendar.add(InlineKeyboardButton('Отмена записи', callback_data='cancel_appointment'))
    if service:
        await call.message.answer(f'Ваше Фамилия и Имя: "{data.get("name_client")}". '
                                  f'\nМастер: "{data.get("name_master")}"'
                                  f'\nУслуга: "{service.name}"', reply_markup=inline_calendar)
    else:
        await call.message.answer(f'Выберите дату.', reply_markup=inline_calendar)


def get_key(d, value):
    for k, v in d.items():
        if v == value:
            return k
