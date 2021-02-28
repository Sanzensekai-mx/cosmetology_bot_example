from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

cancel_add_master = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='Отмена добавления мастера', callback_data='cancel_add_master')
    ]
]
)
