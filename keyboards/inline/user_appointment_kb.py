from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

cancel_appointment = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton('Отмена записи', callback_data='cancel_appointment')
    ]
])


cancel_appointment_or_confirm = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton('Подтвердить', callback_data='confirm_appointment')
    ],
    [
        InlineKeyboardButton('Отмена записи', callback_data='cancel_appointment')
    ]
])
