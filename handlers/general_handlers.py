from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from states.user_states import UserAppointment, UserServices
from states.admin_states import AdminAddMaster, AdminAddService, AdminDelService

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
