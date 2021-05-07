import os
import calendar

import pytz
from dotenv import load_dotenv

load_dotenv(encoding='utf-8')

BOT_TOKEN = str(os.environ.get('BOT_TOKEN'))  # Dashboard
# BOT_TOKEN = str(os.getenv("BOT_TOKEN"))
admins = str(os.environ.get('admins')).split(', ')   # Dashboard
# admins = str(os.getenv("admins")).split(', ')
masters_id = str(os.environ.get('masters_id')).split(', ')   # Dashboard
# masters_id = str(os.getenv("masters_id")).split(',')
# masters_username = str(os.getenv("masters_username")).split(', ')

# host = str(os.getenv("PG_HOST"))  # хост базы данных
# PG_USER = str(os.getenv("PG_USER"))  # имя владельца базы данных
# PG_PASS = str(os.getenv("PG_PASS"))  # пароль бд
# DATABASE = str(os.getenv("DATABASE"))  # имя БД в pgAdmin

# ip = str(os.environ.get("ip"))

# Ссылка подключения к базе данных
# POSTGRES_URI = str(os.environ.get('DATABASE_URL'))
POSTGRES_URI = str('postgres://eonygkthshbtam:31ee6008fc438b23767c794c6937c7ab0927dcf1d4d4d6f050af74a9034ac9f7@ec2-34-201-248-246.compute-1.amazonaws.com:5432/d147m0tihn255k')
# masters_and_id = {m_name: m_id for m_name in masters_username for m_id in masters_id}
# masters_and_id = dict(zip(masters_username, masters_id))
rus_months = ['', 'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
              'Июль', 'Август', 'Сентябрь',  'Октябрь', 'Ноябрь', 'Декабрь']
eng_days = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']
rus_days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']

months = {calendar.month_name[i]: rus_months[i] for i in range(13)}
days = {eng_days[i]: rus_days[i] for i in range(7)}
tz_ulyanovsk = pytz.timezone('Europe/Ulyanovsk')
