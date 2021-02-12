from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

phone_number = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton('Отправить номер телефона', request_contact=True)
    ]
], resize_keyboard=True)
