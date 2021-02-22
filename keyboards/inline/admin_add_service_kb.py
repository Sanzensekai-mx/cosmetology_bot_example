from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

cancel_add_service = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='Отмена добавления услуги', callback_data='cancel_add_service')
    ]
]
)
