import datetime
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from states.user_states import UserAppointment, UserServices
from states.admin_states import AdminAddMaster, AdminAddService, AdminDelService, AdminCheckLog, AdminDelLog
from utils.general_func import date_process_enter
from keyboards.default import admin_default_cancel_back_check_log, default_cancel_appointment

from loader import dp, bot


@dp.callback_query_handler(text_contains='page',
                           state=[UserAppointment, AdminAddService, AdminAddMaster, UserServices, AdminDelService])
async def process_callback_page_button(callback: CallbackQuery, state: FSMContext):
    await callback.answer(cache_time=60)
    if callback.data == 'next_page':
        async with state.proxy() as data_from_state:
            data_from_state['page'] += 1
        data_from_state = await state.get_data()
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
        await callback.message.answer(data_from_state.get('all_result_messages')[data_from_state.get('page')],
                                      reply_markup=data_from_state.get('keyboards')[data_from_state.get('page')])
    elif callback.data == 'pre_page':
        async with state.proxy() as data_from_state:
            data_from_state['page'] -= 1
        data_from_state = await state.get_data()
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
        await callback.message.answer(data_from_state.get('all_result_messages')[data_from_state.get('page')],
                                      reply_markup=data_from_state.get('keyboards')[data_from_state.get('page')])


@dp.callback_query_handler(state=[AdminCheckLog, AdminDelLog, UserAppointment.Date], text_contains='wrong_date')
async def wrong_date_process(call: CallbackQuery):
    await call.answer(cache_time=60)
    await call.message.answer('Дата неактуальна, выберите не пустую дату.')


@dp.callback_query_handler(state=[AdminCheckLog.CheckMonths, AdminDelLog.ChoiceDate, UserAppointment.Date],
                           text_contains='month_')
async def change_month_process(call: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    # print(k)
    await call.answer(cache_time=60)
    data = await state.get_data()
    current_date = datetime.date.today()
    result, service_state = call.data.split('_')[1], call.data.split('_')[2]
    if service_state == 'appointment':
        service_state = True
    elif service_state == 'checks':
        service_state = False
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
        if service_state:
            await call.message.answer('Выбор даты оказания услуги', reply_markup=default_cancel_appointment)
        else:
            await call.message.answer('Записи по месяцам', reply_markup=admin_default_cancel_back_check_log)
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id - 1)
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        if current_state == 'AdminCheckLog:CheckMonths':
            await date_process_enter(call=call, state=state,
                                     year=choice_year,
                                     month=choice_month,
                                     day=1, service=service_state, is_it_for_master=True)
        else:
            await date_process_enter(call=call, state=state,
                                     year=choice_year,
                                     month=choice_month,
                                     day=1, service=service_state)
    elif result == 'previous':
        if choice_month == 1:
            choice_year = choice_year - 1
            choice_month = 12
        else:
            choice_month = int(choice_month) - 1
        data['current_choice_year'] = choice_year
        data['current_choice_month'] = choice_month
        await state.update_data()
        if service_state:
            await call.message.answer('Выбор даты оказания услуги', reply_markup=default_cancel_appointment)
        else:
            await call.message.answer('Записи по месяцам', reply_markup=admin_default_cancel_back_check_log)
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id - 1)
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        if current_state == 'AdminCheckLog:CheckMonths':
            await date_process_enter(call=call, state=state,
                                     year=choice_year,
                                     month=choice_month,
                                     day=1, service=service_state, is_it_for_master=True)
        else:
            await date_process_enter(call=call, state=state,
                                     year=choice_year,
                                     month=choice_month,
                                     day=1, service=service_state)
