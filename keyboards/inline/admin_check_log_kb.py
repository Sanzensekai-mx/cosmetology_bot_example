from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

check_logs_choice_range = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton('Записи на сегодняшний день', callback_data='logs_today')
    ],
    [
        InlineKeyboardButton('Записи на неделю', callback_data='logs_week')
    ],
    [
        InlineKeyboardButton('Записи по месяцам', callback_data='logs_months')
    ],
    [
        InlineKeyboardButton('Отмена просмотра', callback_data='cancel_check')
    ]
])
