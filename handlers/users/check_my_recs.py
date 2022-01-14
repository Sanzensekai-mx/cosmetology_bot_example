import logging

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, InlineKeyboardMarkup, \
    InlineKeyboardButton, CallbackQuery

from keyboards.default import main_menu_client, default_cancel_user_check_logs
from loader import dp
from states.user_states import UserCheckLog
from utils.db_api.models import DBCommands

# from data.config import masters_and_id

db = DBCommands()

logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] '
                           u'#%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO)


# Способ с inline-клавиатурой Закрытия просмотра записей

# @dp.callback_query_handler(state=UserCheckLog.Check, text_contains='cancel_check_user_log')
# async def inline_process_cancel_check_logs(call: CallbackQuery, state: FSMContext):
#     await call.answer(cache_time=60)
#     logging.info(f'from: {call.message.chat.full_name}, text: {call.message.text}, info: Отмена просмотра записей '
#                  f'пользоватем.')
#     await call.message.answer('Отмена просмотра записей.'
#                               '\nВыберите кнопку ниже.', reply_markup=main_menu_client)
#     await state.reset_state()


@dp.message_handler(Text(equals=['Закрыть просмотр записей']), state=UserCheckLog.Check)
async def default_process_cancel_check_logs(message: Message, state: FSMContext):
    await message.answer('Отмена просмотра записей.'
                         '\nВыберите кнопку ниже.', reply_markup=main_menu_client)
    await state.reset_state()


@dp.message_handler(Text(equals='Мои записи'))
async def check_users_logs(message: Message, state: FSMContext):
    # print(await db.get_old_datetime(full_datetime.date.today()))
    await UserCheckLog.Check.set()
    logging.info(f'from: {message.chat.full_name}, text: {message.text.upper()}')
    recs_list = await db.get_all_recs_by_user_id(message.chat.id)
    kb_logs = InlineKeyboardMarkup(row_width=5)
    await state.update_data(
        {'user_logs': {}}
    )
    if not recs_list:
        await message.answer('Вы еще не записывались. \nДля записи нажмите кнопку "Запись"',
                             reply_markup=main_menu_client)
        await state.finish()
    else:
        data = await state.get_data()
        for num, rec in enumerate(recs_list, 1):
            #     date = [x.strip('()').strip() for x in rec.date.split(',')]
            full_datetime = rec.full_datetime
            data['user_logs'][num] = {'full_datetime': rec.full_datetime, 'name_master': rec.name_master}
            kb_logs.add(InlineKeyboardButton(
                f'Дата: {str(full_datetime.day).rjust(2, "0")}.{str(full_datetime.month).rjust(2, "0")}.{full_datetime.year} | '
                f'Время: {full_datetime.hour}:{str(full_datetime.minute).ljust(2, "0")}',
                callback_data=f'ud_{num}'))
        # kb_logs.add(InlineKeyboardButton(f'Закрыть просмотр записей', callback_data='cancel_check_user_log'))
        await state.update_data(data)
        await message.answer('Нажмите на кнопки ниже, чтобы просмотреть подробную информацию о ваших записях.',
                             reply_markup=default_cancel_user_check_logs)
        await message.answer('Ваши записи:', reply_markup=kb_logs)


@dp.callback_query_handler(text_contains='ud_', state=UserCheckLog.Check)
async def process_one_log(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    num = int(call.data.split('_')[1])  # Порядковый номер записи из словаря записей пользователя
    data = await state.get_data()
    choice_log_datetime, choice_master = data['user_logs'][num]['full_datetime'], data['user_logs'][num]['name_master']
    rec = await db.get_rec_by_full_datetime(choice_log_datetime, choice_master)
    # date = [int(d.strip()) for d in rec.date.strip('()').split(',')]
    full_datetime = rec.full_datetime
    service = await db.get_service(rec.service)
    # Кнопка со ссылкой на описание и фото услуги?
    # kb_log_cancel = InlineKeyboardMarkup().add(InlineKeyboardButton(
    #     f'Закрыть просмотр записей', callback_data='cancel_check_user_log'))
    await call.message.answer(
        f'''
Время - {rec.time.strftime("%H:%M")}\n
Дата - {str(full_datetime.day).rjust(2, "0")}.{str(full_datetime.month).rjust(2, "0")}.{full_datetime.year}\n
Имя клиента - {rec.name_client}\n
Мастер - {choice_master}\n
Услуга - {rec.service}\n
Стоимость - {service.price}''')
    # await state.finish()
    # Добавить кнопку-ссылку на пост в инстаграмм об услуге или показать описание услуги
