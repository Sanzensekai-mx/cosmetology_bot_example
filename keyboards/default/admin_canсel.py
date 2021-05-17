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

admin_default_cancel_del_master = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton('Отмена удаления мастера')
        ]
    ], resize_keyboard=True)

admin_default_cancel_confirm_service = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton('Подтвердить добавление услуги')
        ],
        [
            KeyboardButton('Отмена добавления услуги')
        ]
    ], resize_keyboard=True)

admin_default_cancel_service = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton('Отмена добавления услуги')
        ]
    ], resize_keyboard=True)

admin_default_cancel_confirm_masters_list = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton('Подтвердить список мастеров')
        ],
        [
            KeyboardButton('Отмена добавления услуги')
        ]
    ], resize_keyboard=True
)

admin_default_cancel_del_service = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton('Отмена удаления услуги')
        ]
    ], resize_keyboard=True)

admin_default_cancel_mailing = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton('Отмена рассылки')
        ]
    ], resize_keyboard=True)

admin_default_cancel_check_log = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton('Отмена просмотра')
        ]
    ], resize_keyboard=True)

admin_default_cancel_back_check_log = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton('Назад в главное меню просмотра записей')
        ],
        [
            KeyboardButton('Отмена просмотра')
        ]
    ], resize_keyboard=True)

admin_default_cancel_del_log = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton('Закрыть меню удаления записей')
        ]
    ], resize_keyboard=True)
