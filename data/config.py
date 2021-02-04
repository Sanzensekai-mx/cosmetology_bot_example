import os

# load_dotenv()
BOT_TOKEN = str(os.environ.get('BOT_TOKEN'))
admins = str(os.environ.get('admins')).split(', ')
POSTGRES_URI = str(os.environ.get('DATABASE_URL'))  # Для Heroku

# host = str(os.environ.get("PG_HOST"))  # хост базы данных
# PG_USER = str(os.environ.get("PG_USER"))  # имя владельца базы данных
# PG_PASS = str(os.environ.get("PG_PASS"))  # пароль бд
# DATABASE = str(os.environ.get("DATABASE"))  # имя БД в pgAdmin
#
# # ip = str(os.environ.get("ip"))
#
# # Ссылка подключения к базе данных
# POSTGRES_URI = f"postgresql://{PG_USER}:{PG_PASS}@{host}/{DATABASE}"

