from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


admin_cancel_mail_or_confirm = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="/cancel_mail")
        ],
        [
            KeyboardButton(text='Подтвердить')
        ]
    ],
    resize_keyboard=True
)
admin_cancel_mail = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="/cancel_mail")
        ]
    ],
    resize_keyboard=True
)
