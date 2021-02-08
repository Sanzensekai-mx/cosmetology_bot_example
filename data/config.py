import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
admins = str(os.getenv('admins')).split(', ')

host = str(os.getenv("PG_HOST"))  # хост базы данных
PG_USER = str(os.getenv("PG_USER"))  # имя владельца базы данных
PG_PASS = str(os.getenv("PG_PASS"))  # пароль бд
DATABASE = str(os.getenv("DATABASE"))  # имя БД в pgAdmin

# ip = str(os.environ.get("ip"))

# Ссылка подключения к базе данных
POSTGRES_URI = f"postgresql://{PG_USER}:{PG_PASS}@{host}/{DATABASE}"
masters = ['Sanzensekai']
masters_and_id = {master: admin_id for master in masters for admin_id in admins}
