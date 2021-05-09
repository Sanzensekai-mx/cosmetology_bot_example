from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

admin_mailing_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='Медиа (Фото/Видео)', callback_data='send_media')
    ],
    [
        InlineKeyboardButton(text='Документ/Аудио/Гиф/Стикер/Войс/ВидеоКруг',
                             callback_data='send_another')
    ],
    [
        InlineKeyboardButton(text='Пересланный пост/сообщение', callback_data='send_forward')
    ],
    [
        InlineKeyboardButton(text='Обычный текст', callback_data='send_text')
    ],
])


cancel_mailing_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='Отмена рассылки', callback_data='cancel_mail')
    ]
])
