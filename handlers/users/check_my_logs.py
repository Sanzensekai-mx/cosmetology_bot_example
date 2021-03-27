import logging
import datetime
import calendar
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, ReplyKeyboardRemove, InlineKeyboardMarkup, \
    InlineKeyboardButton, CallbackQuery, ContentType

from keyboards.default import main_menu_client
from keyboards.inline import check_logs_choice_range
from loader import dp
from states.user_states import UserCheckLog
from utils.db_api.models import DBCommands
# from data.config import masters_and_id

db = DBCommands()

logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] '
                           u'#%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO)


@dp.callback_query_handler(state=UserCheckLog.Check, text_contains='cancel_check_user_log')
async def process_cancel_check_logs(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    logging.info(f'from: {call.message.chat.full_name}, text: {call.message.text}, info: Отмена добавления услуги.')
    await call.message.answer('Отмена добавления нового мастера.', reply_markup=main_menu_client)
    await state.reset_state()


@dp.message_handler(Text(equals='Мои записи'))
async def check_users_logs(message: Message, state: FSMContext):
    # print(await db.get_old_datetime(datetime.date.today()))
    await UserCheckLog.Check.set()
    logging.info(f'from: {message.chat.first_name}, text: {message.text}')
    logs_list = await db.get_all_logs_by_user_id(message.chat.id)
    kb_logs = InlineKeyboardMarkup(row_width=5)
    await state.update_data(
        {'user_logs': {}}
    )
    if not logs_list:
        await message.answer('Вы еще не записывались. \nДля записи нажмите кнопку "Запись"',
                             reply_markup=main_menu_client)
        await state.finish()
    # print(logs_list[0].full_datetime)
    # print(type(logs_list[0].full_datetime))
    else:
        data = await state.get_data()
        for num, log in enumerate(logs_list, 1):
        # Список вида (2021, 2, 22, 0) 10:00
            date = [x.strip('()').strip() for x in log.date.split(',')]
            data['user_logs'][num] = {'datetime': f'{log.full_datetime}', 'name_master': f'{log.name_master}'}
            kb_logs.add(InlineKeyboardButton(f'Дата:  {date[2]} / {date[1]} / {date[0]} Время: {log.time}',
                                             callback_data=f'ud_{num}'))
        kb_logs.add(InlineKeyboardButton(f'Закрыть просмотр записей', callback_data='cancel_check_user_log'))
        await state.update_data(data)
        await message.answer('Ваши записи:', reply_markup=kb_logs)


@dp.callback_query_handler(text_contains='ud_', state=UserCheckLog.Check)
async def process_one_log(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    num = int(call.data.split('_')[1])  # Порядковый номер записи из словаря записей пользователя
    data = await state.get_data()
    choice_log_datetime, choice_master = data['user_logs'][num]['datetime'], data['user_logs'][num]['name_master']
    log = await db.get_log_by_full_datetime(choice_log_datetime, choice_master)
    date = [int(d.strip()) for d in log.date.strip('()').split(',')]
    service = await db.get_service(log.service)
    # Кнопка со ссылкой на описание и фото услуги?
    await call.message.answer(
        f'''
Время - {log.time}\n
Дата - {date[2]} / {date[1]} / {date[0]}\n
Имя клиента - {log.name_client}\n
Мастер - {choice_master}\n
Услуга - {log.service}\n
Стоимость - {service.price}''')
    await state.finish()
    # Добавить кнопку-ссылку на пост в инстаграмм об услуге или показать описание услуги
