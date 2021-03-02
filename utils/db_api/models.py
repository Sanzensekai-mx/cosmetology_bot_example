import datetime
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
    master = db.Column(db.String)
    datetime = db.Column(db.String)
    time = db.Column(db.JSON, nullable=False, server_default="{}")


class Master(db.Model):
    __tablename__ = 'masters'
    id = db.Column(db.Integer, db.Sequence('master_id_seq'), primary_key=True)
    master_name = db.Column(db.String)
    master_user_id = db.Column(db.BigInteger, unique=True)
    master_services = db.Column(db.String)


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
        service = await self.get_service(service_name)
        if service:
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
    async def get_log_by_client(name_client):
        log = await Log.query.where(Log.name_client == name_client).gino.first()
        return log

    @staticmethod
    async def get_log_by_full_datetime(full_datetime, master):
        logs = await Log.query.where(Log.full_datetime == full_datetime).gino.all()
        # log = await Log.query.where(Log.name_master == master).gino.first()
        if logs:
            for log in logs:
                # if log.full_datetime == full_datetime:
                if log.name_master == master:
                    return log
        # return log

    async def del_log(self, full_datetime, master):
        log = await self.get_log_by_full_datetime(full_datetime, master)
        if log:
            await log.delete()
            # return log
        # return log

    @staticmethod
    async def get_old_logs(current_date):
        # year, month, day = current_date.year, current_date.month, current_date.day
        # c = calendar.LocaleTextCalendar(calendar.MONDAY, locale='Russian_Russia')
        # current_date_with_weekdays = [date for date in c.itermonthdays4(year, month) if date[2] == day][0]
        logs = []
        for log in await Log.query.gino.all():
            date_process = [int(d.strip()) for d in str(log.date).strip('()').split(',')]
            date = datetime.date(date_process[0], date_process[1], date_process[2])
            if date < current_date:
                logs.append(log)
        # logs = await Log.query.where(Log.date < current_date_with_weekdays).gino.all()
        return logs

    @staticmethod
    async def get_logs_only_date(date, master):
        logs_list = await Log.query.where(Log.date == date).gino.all()
        return_logs = []
        for line in logs_list:
            if line.name_master == master and line.date == date:
                return_logs.append(line)
        return return_logs

    @staticmethod
    async def is_client_full_datetime_in_db(full_datetime, name_client):
        logs = await Log.query.where(Log.full_datetime == full_datetime).gino.all()
        for log in logs:
            if log.name_client == name_client:
                return True
        return False

    async def is_this_log_in_db(self, name_client):
        log = await self.get_log_by_full_datetime(name_client)
        if log:
            return True
        return False

    @staticmethod
    async def is_this_log_5_in_db(user_id):
        log = await Log.query.where(Log.user_id == user_id).gino.first()
        if log:
            num_one_user_id = 0
            for i in [log.user_id for log in await Log.query.gino.all()]:
                if i == log.user_id:
                    num_one_user_id += 1
                if num_one_user_id == 5:
                    return True
        return False

    @staticmethod
    async def get_all_logs_by_user_id(user_id):
        logs = await Log.query.where(Log.user_id == user_id).gino.all()
        return logs

    async def add_log(self, user_id, name_client, name_master, service, full_datetime, date, time, phone_number):
        log_one = await self.get_log_by_full_datetime(full_datetime, name_master)
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
    async def get_datetime(datetime_one, master):
        # datetime_list = await Datetime.query.where(Datetime.datetime == datetime).gino.all()
        datetime_list = await Datetime.query.where(Datetime.master == master).gino.all()
        # datetime_with_master =
        for line in datetime_list:
            if line.datetime == datetime_one:
                return line

    @staticmethod
    async def get_old_datetime(current_date):
        datetime_many = []
        for date_one in await Datetime.query.gino.all():
            date_process = [int(d.strip()) for d in str(date_one.datetime).strip('()').split(',')]
            date = datetime.date(date_process[0], date_process[1], date_process[2])
            if date < current_date:
                datetime_many.append(date_one)
        # logs = await Log.query.where(Log.date < current_date_with_weekdays).gino.all()
        return datetime_many

    async def del_datetime(self, datetime_one, master):
        datetime_first = await self.get_datetime(datetime_one, master)
        if datetime_first:
            await datetime_first.delete()
            return datetime_first
        return datetime_first

    async def get_dict_of_time(self, datetime_one, master):
        datetime_first = await self.get_datetime(datetime_one, master)
        return datetime_first.time

    async def add_log_datetime(self, datetime_one, master):
        datetime_first = await self.get_datetime(datetime_one, master)
        if datetime_first:
            return True
        datetime_first = Datetime()
        datetime_first.datetime = datetime_one
        datetime_first.master = master
        datetime_first.time = {'10:00': False, '10:30': False, '11:00': False, '11:30': False,
                               '12:00': False, '12:30': False, '13:00': False, '13:30': False,
                               '14:00': False, '14:30': False, '15:00': False, '15:30': False,
                               '16:00': False, '16:30': False, '17:00': False}
        await datetime_first.create()
        return False

    async def add_update_date(self, datetime_one, time, master):
        datetime_first = await self.get_datetime(datetime_one, master)
        if datetime_first:
            dict_time = datetime_first.time
            dict_time[time] = True
            await datetime_first.update(
                id=datetime_first.id,
                master=datetime_first.master,
                datetime=datetime_first.datetime,
                time=dict_time
            ).apply()
            return datetime_first
        datetime_first = Datetime()
        datetime_first.master = master
        datetime_first.datetime = datetime_one
        datetime_first.time = time
        await datetime_first.create()
        return datetime_first

        # Методы таблицы masters
    @staticmethod
    async def get_master(master_name):
        master = await Master.query.where(Master.master_name == master_name).gino.first()
        return master

    async def is_this_master_in_db(self, master_name):
        master = await self.get_service(master_name)
        if master:
            return True
        return False

    @staticmethod
    async def all_masters():
        masters = await Master.query.gino.all()
        return masters

    async def add_master(self, master_name, master_user_id, master_services):
        old_master = await self.get_master(master_name)
        # Обновляет услугу, если такая уже существует в БД
        if old_master:
            await old_master.update(
                id=old_master.id,
                master_name=master_name,
                master_user_id=int(master_user_id),
                master_services=master_services
            ).apply()
            return old_master
        # Создание новой услуги в БД
        new_master = Master()
        new_master.master_name = master_name
        new_master.master_user_id = int(master_user_id)
        new_master.master_services = master_services
        await new_master.create()
        return new_master
