from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu_no_orders = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu_no_orders.add(KeyboardButton(text="Запись"))
main_menu_no_orders.insert(KeyboardButton(text="Акции"))
main_menu_no_orders.add(KeyboardButton(text='О салоне'))
