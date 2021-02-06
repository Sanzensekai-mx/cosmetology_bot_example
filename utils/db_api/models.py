from aiogram.types import User as User_api_type
from utils.db_api.database import db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, db.Sequence('user_id_seq'), primary_key=True)
    full_name = db.Column(db.String)
    # Идентификатор чата с пользователем
    user_id = db.Column(db.BigInteger, unique=True)
    # Никнейм пользователя
    username = db.Column(db.String)

    def __repr__(self):
        return "<User(id='{}', fullname='{}', username='{}')>".format(
            self.chat_id, self.full_name, self.username)


class Service(db.Model):
    __tablename__ = 'services'
    id = db.Column(db.Integer, db.Sequence('service_id_seq'), primary_key=True)
    name = db.Column(db.String)
    price = db.Column(db.String)
    describe = db.Column(db.String)
    pic_file_id = db.Column(db.String)
    time = db.Column(db.Integer)  # Сколько времени занимает услуга


class Log(db.Model):
    __tablename__ = 'log'
    id = db.Column(db.Integer, db.Sequence('log_id_seq'), primary_key=True)
    name_client = db.Column(db.String)
    name_master = db.Column(db.String)
    date = db.Column(db.String)
    time = db.Column(db.String)
    phone_number = db.Column(db.String)


class DBCommands:
    # Функция возвращает объект из таблицы User,
    # если такой user_id существует в БД.
    # Возвращает None, если такого нет
    @staticmethod
    async def get_user(user_id):
        user = await User.query.where(User.user_id == user_id).gino.first()
        return user

    @staticmethod
    async def all_users():
        users = await User.query.gino.all()
        return users

    async def add_new_user(self):
        user = User_api_type.get_current()
        old_user = await self.get_user(user.id)  # get_user берет в качестве аргумента аттрибут id
        # типа telegram api User
        if old_user:
            return old_user
        new_user = User()
        new_user.user_id = user.id
        new_user.username = user.username
        new_user.full_name = user.full_name
        await new_user.create()
        return new_user

    @staticmethod
    async def count_users() -> int:
        total = await db.func.count(User.id).gino.scalar()
        return total

    # Методы для таблицы services
    @staticmethod
    async def get_service(service_name):
        service = await Service.query.where(Service.name == service_name).gino.first()
        return service

    async def is_this_service_in_db(self, service_name):
        meme = await self.get_service(service_name)
        if meme:
            return True
        return False

    @staticmethod
    async def all_meme():
        items = await Service.query.gino.all()
        return items

    async def add_service(self, service_name, service_describe=None, service_price=None, service_pic_file_id=None,
                          service_time=None):
        old_meme = await self.get_service(service_name)
        # Обновляет мем, если такой уже существует в БД
        if old_meme:
            await old_meme.update(
                id=old_meme.id,
                name=service_name,
                price=service_price,
                describe=service_describe,
                pic_href=service_pic_file_id,
                time=service_time
            ).apply()
            return old_meme
        # Создание нового мема в БД
        new_service = Service()
        new_service.name = service_name
        new_service.describe = service_describe
        new_service.pic_file_id = service_pic_file_id
        new_service.price = service_price
        new_service.time = service_time
        await new_service.create()
        return new_service

    # @staticmethod
    # async def show_service_test():
    #     service = await Service.query.gino.first()
    #     return service
