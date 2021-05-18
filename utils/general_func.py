import calendar
import datetime
from math import ceil
import numpy as np
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, InlineKeyboardMarkup, \
    InlineKeyboardButton, CallbackQuery
from utils.db_api.models import DBCommands
from data.config import days, months
from loader import dp, bot

db = DBCommands()


# 1-ый элемент - сообщение, 2-ой - клавиатура
async def return_kb_mes_services(message, state):
    await state.update_data(
        {'services_by_page': {1: {}},
         'keyboards': {1: {}},
         'all_result_messages': {1: {}},
         'page': 1}
    )
    data_from_state = await state.get_data()
    services = await db.all_services()
    if len(services) <= 5:
        choice_service_kb = InlineKeyboardMarkup(row_width=5)
        res_message = ''
        # current_services_dict = {}
        for num, service in enumerate(services, 1):
            res_message += f'{num}. {service.name} - {service.price}\n'
            res_message += '\n'
            data_from_state.get('services_by_page')[1].update({str(num): service.name})
            # current_services_dict[str(num)] = service.name
            choice_service_kb.insert(InlineKeyboardButton(f'{num}',
                                                          callback_data=f's_{num}'))
        data_from_state.get('keyboards').update({1: choice_service_kb})
        data_from_state.get('all_result_messages').update({1: res_message})
        await state.update_data(data_from_state)
    elif len(services) > 5:
        data_from_state.get('services_by_page').clear()
        number_of_pages = ceil(len(services) / 5)
        rule_np_list = []
        for i in range(number_of_pages):
            if i == 0:
                rule_np_list.append(5)
                continue
            rule_np_list.append(rule_np_list[i - 1] + 5)
        services_by_pages = np.array_split(services, rule_np_list)
        keyboards_inside = {}
        for page_num in range(number_of_pages):
            if page_num == 0:
                keyboards_inside.update(
                    {page_num + 1: InlineKeyboardMarkup(row_width=5, inline_keyboard=[
                        [InlineKeyboardButton('➡️', callback_data='next_page')]]
                                                        )})
                continue
            if page_num == list(range(number_of_pages))[-1]:
                keyboards_inside.update(
                    {page_num + 1: InlineKeyboardMarkup(row_width=5, inline_keyboard=[
                        [InlineKeyboardButton('⬅️', callback_data='pre_page')]]
                                                        )})
                continue
            keyboards_inside.update({page_num + 1: InlineKeyboardMarkup(row_width=5, inline_keyboard=[
                [InlineKeyboardButton('⬅️', callback_data='pre_page')],
                [InlineKeyboardButton('➡️', callback_data='next_page')]])})
        for page_num, page in enumerate(range(number_of_pages), 1):
            data_from_state.get('services_by_page').update({page_num: {}})
            res_message = ''
            for num, service in enumerate(list(services_by_pages)[page], 1):
                service_button = InlineKeyboardButton(str(num), callback_data=f's_{num}')
                data_from_state.get('services_by_page')[page_num].update({str(num): service.name})
                if num == 1:
                    keyboards_inside[page_num].add(service_button)
                    res_message += f'{num}. {service.name} - {service.price}\n'
                    res_message += '\n'
                    continue
                keyboards_inside[page_num].insert(service_button)
                res_message += f'{num}. {service.name} - {service.price}\n'
                res_message += '\n'
            res_message += f'Страница {page_num} из {number_of_pages}'
            data_from_state.get('all_result_messages').update({page_num: res_message})
        data_from_state.get('keyboards').update(keyboards_inside)
        await state.update_data(data_from_state)
    await message.answer(
        f"Выберите услугу:\n\n{data_from_state.get('all_result_messages')[data_from_state.get('page')]}",
        reply_markup=data_from_state.get('keyboards')[data_from_state.get('page')])

    # return res_message, choice_service_kb


async def date_process_enter(state, year, month, day, service=True, call=None, message=None):
    response = call.message if call else message
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
        if service:
            inline_calendar.add(InlineKeyboardButton('<', callback_data='month_previous_appointment'))
        else:
            inline_calendar.add(InlineKeyboardButton('<', callback_data='month_previous_checks'))
    data['current_choice_month'] = month
    data['current_choice_year'] = year
    await state.update_data(data)
    inline_calendar.insert(InlineKeyboardButton(f'{months.get(print_c.split()[0])} {print_c.split()[1]}',
                                                callback_data=' '))
    if service:
        inline_calendar.insert(InlineKeyboardButton('>', callback_data='month_next_appointment'))
    else:
        inline_calendar.insert(InlineKeyboardButton('>', callback_data='month_next_checks'))
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
        await response.answer(f'Ваше Фамилия и Имя: "{data.get("name_client")}". '
                              f'\nМастер: "{data.get("name_master")}"'
                              f'\nУслуга: "{service.name}"', reply_markup=inline_calendar)
    else:
        await response.answer(f'Выберите дату.', reply_markup=inline_calendar)


def get_key(d, value):
    for k, v in d.items():
        if v == value:
            return k
