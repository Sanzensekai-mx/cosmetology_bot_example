import logging
from asyncio import sleep

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery, ContentType, \
    InputMediaPhoto, InputMediaVideo, ReplyKeyboardRemove
from loader import dp, bot
from keyboards.default import main_menu_admin, admin_cancel_mail_or_confirm, admin_default_cancel_mailing
from keyboards.inline import admin_mailing_kb, cancel_mailing_kb
from data.config import admins
from states.admin_states import AdminMailing
from utils.db_api.models import DBCommands

db = DBCommands()

logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] '
                           u'%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO)

logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] '
                           u'#%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.ERROR)


@dp.callback_query_handler(text_contains='cancel_mail', chat_id=admins, state=AdminMailing)
async def process_cancel_add_service(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    await call.message.answer('Отмена рассылки.', reply_markup=main_menu_admin)
    await state.reset_state()


@dp.message_handler(Text(equals='Отмена рассылки'), chat_id=admins, state=AdminMailing)
async def cancel_mail(message: Message, state: FSMContext):
    await message.answer('Отмена рассылки.', reply_markup=main_menu_admin)
    await state.reset_state()


@dp.message_handler(Text(equals='Рассылка'), chat_id=admins)
async def mailing(message: Message):
    count_users = await db.count_users()
    logging.info(f'from: {message.chat.full_name}, text: {message.text.upper()}')
    await message.answer("Выберите тип рассылки из меню."
                         f"Сейчас в боте {count_users} пользователя(ей)",
                         reply_markup=admin_default_cancel_mailing)
    await message.answer("Отправить:", reply_markup=admin_mailing_kb)
    await AdminMailing.MailingMenu.set()


@dp.callback_query_handler(text_contains='send', chat_id=admins, state=AdminMailing.MailingMenu)
async def process_callback_data_mailing(call: CallbackQuery):
    await call.answer(cache_time=60)
    what_to_send = call.data.split('_')[1]
    if what_to_send == 'media':
        await AdminMailing.Media.set()
        await call.message.answer('Пришлите нужное количество фото/видео по одной штуке для отправки пользователям '
                                  'группы. Нужную подпись можно будет добавить к одному присланному медиа. Если к '
                                  'нескольким файлам добавить надпись, то её вообще не будет.',
                                  reply_markup=admin_cancel_mail_or_confirm)
    elif what_to_send == 'another':
        await AdminMailing.AnotherMedia.set()
        await call.message.answer('Пришлите документ, аудио, анимацию, стикер, голосовое или видеозаметку. '
                                  '\nЗа раз можно отправить только один объект.')
    elif what_to_send == 'forward':
        await AdminMailing.Forward.set()
        await call.message.answer('Пересланный пост/сообщение')
        await call.message.answer('Перешлите нужный пост в этот диалог. \nИмейте ввиду, что если в посте несколько '
                                  'фото/видео, то пользователям отошлется только первая картинка. Сработает Too '
                                  'many requests.')
    elif what_to_send == 'text':
        await AdminMailing.Text.set()
        await call.message.answer('Обычный текст.', reply_markup=ReplyKeyboardRemove())
        await call.message.answer('Напишите текст для отправки.', reply_markup=cancel_mailing_kb)


async def process_media_send(msg, state):
    data_from_state = await state.get_data()
    if msg.photo:
        data_from_state.get('media_file_id').append(InputMediaPhoto(msg.photo[-1].file_id, caption=msg.caption))
    elif msg.video:
        data_from_state.get('media_file_id').append(InputMediaVideo(msg.video.file_id, caption=msg.caption))
    await state.update_data(data_from_state)
    await state.reset_state(with_data=False)
    await AdminMailing.Media.set()


# Отправить медиагруппу: Фото/Видео/Подпись к ним
@dp.message_handler(chat_id=admins, state=AdminMailing.Media, content_types=[ContentType.PHOTO,
                                                                             ContentType.VIDEO,
                                                                             ContentType.TEXT])
async def send_group_photo(message: Message, state: FSMContext):
    logging.info(message.text)
    data_from_state = await state.get_data()
    if data_from_state.get('media_file_id') is None:
        await state.update_data({'media_file_id': []})
    # else:
    #     print(data_from_state.get('media_file_id'))
    if message.photo or message.video:
        await process_media_send(message, state)
    elif message.text == 'Отменить':
        await message.answer('Отмена рассылки.', reply_markup=main_menu_admin)
        await state.finish()
    elif message.text == 'Подтвердить':
        users_data = await db.all_users()
        for user in users_data:
            try:
                await bot.send_media_group(chat_id=user.user_id, media=data_from_state.get('media_file_id'))
                await sleep(0.3)
            except Exception as error:
                logging.error(f'{error}, User: {user.full_name}, chat_id: {user.user_id}')
                await message.answer(f'{error}, User: {user.full_name}, chat_id: {user.user_id}')
        await message.answer("Рассылка выполнена.", reply_markup=main_menu_admin)
        await state.finish()


# Отправить Документ/Аудио/Анимацию(гифку)/Стикер/Голосовое/Видеозаметку
@dp.message_handler(chat_id=admins, state=AdminMailing.AnotherMedia, content_types=[ContentType.DOCUMENT,
                                                                                    ContentType.AUDIO,
                                                                                    ContentType.ANIMATION,
                                                                                    ContentType.STICKER,
                                                                                    ContentType.VOICE,
                                                                                    ContentType.VIDEO_NOTE])
async def send_another(message: Message, state: FSMContext):
    type_dict_caption = ['audio', 'document', 'animation']
    type_dict_without_caption = ['sticker', 'voice', 'video_note']
    caption_type_from_msg = []
    no_caption_type_from_msg = []
    try:
        caption_type_from_msg = [k for k in message.values.keys() if k in type_dict_caption][0]
    except IndexError:
        no_caption_type_from_msg = [k for k in message.values.keys() if k in type_dict_without_caption][0]
    users_data = await db.all_users()
    type_msg_dict = {}
    if caption_type_from_msg == 'document':
        type_msg_dict['document'] = bot.send_document
        type_msg_dict['file_id'] = message.document.file_id
    elif caption_type_from_msg == 'audio':
        type_msg_dict['audio'] = bot.send_audio
        type_msg_dict['file_id'] = message.audio.file_id
    elif caption_type_from_msg == 'animation':
        type_msg_dict['animation'] = bot.send_animation
        type_msg_dict['file_id'] = message.animation.file_id
    elif no_caption_type_from_msg == 'sticker':
        type_msg_dict['sticker'] = bot.send_sticker
        type_msg_dict['file_id'] = message.sticker.file_id
    elif no_caption_type_from_msg == 'voice':
        type_msg_dict['voice'] = bot.send_voice
        type_msg_dict['file_id'] = message.voice.file_id
    elif no_caption_type_from_msg == 'video_note':
        type_msg_dict['video_note'] = bot.send_video_note
        type_msg_dict['file_id'] = message.video_note.file_id
    for user in users_data:
        try:
            await type_msg_dict[caption_type_from_msg](user.user_id, type_msg_dict['file_id'],
                                                       caption=message.caption) if caption_type_from_msg \
                else await type_msg_dict[no_caption_type_from_msg](user.user_id, type_msg_dict['file_id'])
            await sleep(0.3)
        except Exception as error:
            logging.error(f'{error}, User: {user.full_name}, chat_id: {user.user_id}')
            await message.answer(f'{error}, User: {user.full_name}, chat_id: {user.user_id}')
    await message.answer("Рассылка выполнена.", reply_markup=main_menu_admin)
    await state.finish()


# Отправить обычный текст, без медиа
@dp.message_handler(chat_id=admins, state=AdminMailing.Text, content_types=ContentType.TEXT)
async def send_everyone(message: Message, state: FSMContext):
    text = message.text
    users_data = await db.all_users()
    for user in users_data:
        try:
            await bot.send_message(chat_id=user.user_id,
                                   text=text)
            await sleep(0.3)
        except Exception as error:
            logging.error(f'{error}, User: {user.full_name}, chat_id: {user.user_id}')
            await message.answer(f'{error}, User: {user.full_name}, chat_id: {user.user_id}')
    await message.answer("Рассылка выполнена.", reply_markup=main_menu_admin)
    await state.finish()


# Отправить пересланное сообщение
@dp.message_handler(chat_id=admins, state=AdminMailing.Forward, content_types=ContentType.all())
async def send_forward_message(message: Message, state: FSMContext):
    users_data = await db.all_users()
    for user in users_data:
        try:
            await bot.forward_message(chat_id=user.user_id,
                                      from_chat_id=message.chat.id,
                                      message_id=message.message_id)
            await sleep(2)
        except Exception as error:
            logging.error(f'{error}, User: {user.full_name}, chat_id: {user.user_id}')
            await message.answer(f'{error}, User: {user.full_name}, chat_id: {user.user_id}')
    await message.answer("Рассылка выполнена.", reply_markup=main_menu_admin)
    await state.finish()
