from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu_client = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu_client.add(KeyboardButton(text="Запись"))
main_menu_client.insert(KeyboardButton(text="Мои записи"))
main_menu_client.add(KeyboardButton(text="Акции"))
main_menu_client.insert(KeyboardButton(text='О салоне'))

main_menu_admin = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu_admin.add(KeyboardButton(text='Посмотреть записи ко мне (супер-мастер)'))
main_menu_admin.add(KeyboardButton(text='Добавить услугу'))
main_menu_admin.insert(KeyboardButton(text='Рассылка'))
main_menu_admin.add(KeyboardButton(text="Запись"))
main_menu_admin.insert(KeyboardButton(text="Мои записи"))
main_menu_admin.add(KeyboardButton(text="Акции"))
main_menu_admin.insert(KeyboardButton(text='О салоне'))

main_menu_master = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu_master.add(KeyboardButton(text='Посмотреть записи ко мне (мастер)'))
main_menu_master.add(KeyboardButton(text="Запись"))
main_menu_master.insert(KeyboardButton(text="Мои записи"))
main_menu_master.add(KeyboardButton(text="Акции"))
main_menu_master.insert(KeyboardButton(text='О салоне'))
