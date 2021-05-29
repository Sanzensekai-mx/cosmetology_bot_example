import os
import calendar

# from dotenv import load_dotenv

# load_dotenv(encoding='utf-8')

BOT_TOKEN = str(os.environ.get('BOT_TOKEN'))  # Dashboard Heroku
# BOT_TOKEN = str(os.getenv("BOT_TOKEN"))
admins = str(os.environ.get('admins')).split(', ')   # Dashboard Heroku
# admins = str(os.getenv("admins")).split(', ')
masters_id = str(os.environ.get('masters_id')).split(', ')   # Dashboard Heroku
# masters_id = str(os.getenv("masters_id")).split(',')

# Ссылка подключения к базе данных
POSTGRES_URI = str(os.environ.get('DATABASE_URL'))  # Dashboard Heroku
# POSTGRES_URI = str(os.getenv("DATABASE_URL"))

rus_months = ['', 'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
              'Июль', 'Август', 'Сентябрь',  'Октябрь', 'Ноябрь', 'Декабрь']
eng_days = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']
rus_days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']

months = {calendar.month_name[i]: rus_months[i] for i in range(13)}
days = {eng_days[i]: rus_days[i] for i in range(7)}
