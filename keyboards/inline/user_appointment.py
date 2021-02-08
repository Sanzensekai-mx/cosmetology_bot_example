from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

cancel_appointment = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton('Отмена записи', callback_data='cancel_appointment')
    ]
])
