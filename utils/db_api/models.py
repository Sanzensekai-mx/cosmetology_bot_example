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
    id = db.Column(db.Integer, db.Sequence('user_id_seq'), primary_key=True)
    name = db.Column(db.String)
    price = db.Column(db.String)
    time = db.Column(db.Integer)  # Сколько времени занимает услуга


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
