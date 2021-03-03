import os
from dotenv import load_dotenv

load_dotenv(encoding='utf-8')
BOT_TOKEN = os.getenv('BOT_TOKEN')  # Dashboard
admins = str(os.getenv('admins')).split(', ')   # Dashboard
masters_id = str(os.getenv('masters_id')).split(', ')   # Dashboard
# masters_username = str(os.getenv("masters_username")).split(', ')

host = str(os.getenv("PG_HOST"))  # хост базы данных
PG_USER = str(os.getenv("PG_USER"))  # имя владельца базы данных
PG_PASS = str(os.getenv("PG_PASS"))  # пароль бд
DATABASE = str(os.getenv("DATABASE"))  # имя БД в pgAdmin

# ip = str(os.environ.get("ip"))

# Ссылка подключения к базе данных
POSTGRES_URI = f"postgresql://{PG_USER}:{PG_PASS}@{host}/{DATABASE}" # Dashboard
# masters_and_id = {m_name: m_id for m_name in masters_username for m_id in masters_id}
# masters_and_id = dict(zip(masters_username, masters_id))
