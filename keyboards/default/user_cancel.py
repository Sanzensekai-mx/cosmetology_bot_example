from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

default_cancel_appointment = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton('Отмена записи')
        ]
    ], resize_keyboard=True)

default_cancel_appointment_confirm = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton('Подтвердить')
        ],
        [
            KeyboardButton('Отмена записи')
        ]
    ], resize_keyboard=True)

default_cancel_user_check_logs = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton('Закрыть просмотр записей')
        ]
    ], resize_keyboard=True)
