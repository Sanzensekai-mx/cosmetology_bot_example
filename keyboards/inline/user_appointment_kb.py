from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

inline_cancel_appointment = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton('Отмена записи', callback_data='cancel_appointment')
    ]
])


inline_cancel_appointment_or_confirm = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton('Подтвердить', callback_data='confirm_appointment')
    ],
    [
        InlineKeyboardButton('Отмена записи', callback_data='cancel_appointment')
    ]
])
