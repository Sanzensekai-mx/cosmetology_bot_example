from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

admin_cancel_mail_or_confirm = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Отменить")
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

admin_default_cancel_add_master = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton('Отмена добавления мастера')
        ]
    ], resize_keyboard=True)

admin_default_cancel_confirm_add_master = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton('Подтвердить добавление')
        ],
        [
            KeyboardButton('Отмена добавления мастера')
        ]
    ], resize_keyboard=True)

admin_default_cancel_confirm_service_list = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton('Подтвердить список сервисов')
        ],
        [
            KeyboardButton('Отмена добавления мастера')
        ]
    ], resize_keyboard=True
)