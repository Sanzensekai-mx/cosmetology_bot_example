import json
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
    user_id = db.Column(db.BigInteger)
    name_client = db.Column(db.String)
    name_master = db.Column(db.String)
    service = db.Column(db.String)
    full_datetime = db.Column(db.String)
    date = db.Column(db.String)
    time = db.Column(db.String)
    phone_number = db.Column(db.String)


class Datetime(db.Model):
    __tablename__ = 'datetime'
    id = db.Column(db.Integer, db.Sequence('datetime_id_seq'), primary_key=True)
    # year = db.Column(db.Integer)
    # month = db.Column(db.Integer)
    # day = db.Column(db.Integer)
    datetime = db.Column(db.String)
    time = db.Column(db.JSON, nullable=False, server_default="{}")


class DBCommands:
    # Методы для таблицы users
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
    async def all_services():
        items = await Service.query.gino.all()
        return items

    async def add_service(self, service_name, service_describe=None, service_price=None, service_pic_file_id=None,
                          service_time=None):
        old_service = await self.get_service(service_name)
        # Обновляет услугу, если такая уже существует в БД
        if old_service:
            await old_service.update(
                id=old_service.id,
                name=service_name,
                price=service_price,
                describe=service_describe,
                pic_href=service_pic_file_id,
                time=service_time
            ).apply()
            return old_service
        # Создание новой услуги в БД
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
    # Методы для таблицы log
    @staticmethod
    async def get_log(full_datetime):
        log = await Log.query.where(Log.full_datetime == full_datetime).gino.first()
        return log

    async def is_this_log_in_db(self, name_client):
        log = await self.get_log(name_client)
        if log:
            return True
        return False

    async def is_this_log_5_in_db(self, name_client):
        log = await self.get_log(name_client)
        if log:
            num_one_user_id = 0
            for i in [log.user_id for log in await Log.query.gino.all()]:
                if i == log.user_id:
                    num_one_user_id += 1
                if num_one_user_id == 5:
                    return True
        return False

    async def add_log(self, user_id, name_client, name_master, service, full_datetime, date, time, phone_number):
        log_one = await self.get_log(name_client)
        # full_log_one = await self.full_get_log(user_id, name_client, name_master, service, date, time, phone_number)
        if log_one:
            await log_one.update(
                id=log_one.id,
                user_id=log_one.user_id,
                name_client=log_one.name_client,
                name_master=log_one.name_master,
                service=log_one.service,
                full_datetime=log_one.full_datetime,
                date=log_one.date,
                time=log_one.time,
                phone_number=log_one.phone_number
            ).apply()
            return log_one
        new_log = Log()
        new_log.user_id = user_id
        new_log.name_client = name_client
        new_log.name_master = name_master
        new_log.service = service
        new_log.full_datetime = full_datetime
        new_log.date = date
        new_log.time = time
        new_log.phone_number = phone_number
        await new_log.create()
        return new_log

    # Мeтоды для таблицы datetime
    @staticmethod
    async def get_datetime(datetime):
        datetime = await Datetime.query.where(Datetime.datetime == datetime).gino.first()
        return datetime

    async def get_dict_of_time(self, datetime):
        datetime_one = await self.get_datetime(datetime)
        return datetime_one.time

    async def add_log_datetime(self, datetime):
        datetime_one = await self.get_datetime(datetime)
        if datetime_one:
            return datetime_one
        datetime_one = Datetime()
        datetime_one.datetime = datetime
        datetime_one.time = {'10:00': False, '10:30': False, '11:00': False, '11:30': False,
                             '12:00': False, '12:30': False, '13:00': False, '13:30': False,
                             '14:00': False, '14:30': False, '15:00': False, '15:30': False,
                             '16:00': False, '16:30': False, '17:00': False}
        await datetime_one.create()
        return datetime_one

    async def add_update_date(self, datetime, time):
        datetime_one = await self.get_datetime(datetime)
        dict_time = datetime_one.time
        dict_time[time] = True
        if datetime_one:
            dict_time = datetime_one.time
            dict_time[time] = True
            await datetime_one.update(
                id=datetime_one.id,
                datetime=datetime_one.datetime,
                time=dict_time
            ).apply()
            return datetime_one
        datetime_one = Datetime()
        datetime_one.datetime = datetime
        datetime_one.time = time
        await datetime_one.create()
        return datetime_one
