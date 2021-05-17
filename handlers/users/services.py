import logging
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, ReplyKeyboardRemove, InlineKeyboardMarkup, \
    InlineKeyboardButton, CallbackQuery

from keyboards.default import default_cancel_show_services, main_menu_client, default_cancel_back_show_services
from loader import dp, bot
from states.user_states import UserServices
from utils.db_api.models import DBCommands
from utils.general_func import return_kb_mes_services

db = DBCommands()


async def process_show_menu_services(message: Message, state: FSMContext):
    # services_mes, services_kb = await return_kb_mes_services(state=state)
    # data = await state.get_data()
    await message.answer('Выберите интересующую вас услугу.', reply_markup=default_cancel_show_services)
    await return_kb_mes_services(message, state)
    # await message.answer(data.get('all_result_messages')[data.get('page')],
    #                      reply_markup=data.get('keyboards')[data.get('page')])
    # await message.answer(services_mes, reply_markup=services_kb)


@dp.message_handler(Text(equals=['Закрыть просмотр услуг']), state=UserServices)
async def cancel_show_services(message: Message, state: FSMContext):
    await message.answer('Отмена просмотра услуг.', reply_markup=main_menu_client)
    await state.reset_state()


@dp.message_handler(Text(equals=['Услуги']))
async def start_show_services(message: Message, state: FSMContext):
    logging.info(f'from: {message.chat.full_name}, text: {message.text.upper()}')
    # await state.update_data({'current_services_dict': {}})
    await process_show_menu_services(message=message, state=state)
    await UserServices.ServicesList.set()


@dp.message_handler(Text(equals=['Вернуться к списку услуг']), state=UserServices.ServicesList)
async def show_services_again(message: Message, state: FSMContext):
    await process_show_menu_services(message=message, state=state)
    await UserServices.ServicesList.set()


@dp.callback_query_handler(state=UserServices.ServicesList, text_contains='s_')
async def process_choice_service(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    service_num = call.data.split('_')[1]
    await call.answer(cache_time=60)
    all_services_names = data.get('services_by_page')[data.get('page')]
    chosen_service = await db.get_service(all_services_names[service_num])
    await bot.send_photo(chat_id=call.message.chat.id, photo=chosen_service.pic_file_id)
    await call.message.answer(text=f'{chosen_service.name}. Цена: {chosen_service.price} рублей.',
                              reply_markup=default_cancel_back_show_services)
    await call.message.answer(text=chosen_service.describe)
