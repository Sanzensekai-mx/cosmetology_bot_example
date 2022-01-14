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
        return f"<User(user_id='{self.user_id}', full_name='{self.full_name}', username='{self.username}')>"


class Service(db.Model):
    __tablename__ = 'services'
    id = db.Column(db.Integer, db.Sequence('service_id_seq'), primary_key=True)
    name = db.Column(db.String)
    price = db.Column(db.String)
    describe = db.Column(db.String)
    pic_file_id = db.Column(db.String)
    time = db.Column(db.Integer)  # Сколько времени занимает услуга

    def __repr__(self):
        return f"<Service(name='{self.name}', price='{self.price}', time='{self.time}')>"


class Records(db.Model):
    __tablename__ = 'records'
    id = db.Column(db.Integer, db.Sequence('log_id_seq'), primary_key=True)
    user_id = db.Column(db.BigInteger)
    name_client = db.Column(db.String)
    name_master = db.Column(db.String)
    service = db.Column(db.String)
    full_datetime = db.Column(db.DateTime)
    date = db.Column(db.Date)
    time = db.Column(db.Time)
    phone_number = db.Column(db.String)

    def __repr__(self):
        return f"<Records(user_id='{self.user_id}', name_client='{self.name_client}', name_master='{self.name_master}', " \
               f"service='{self.service}', full_datetime='{self.full_datetime}', phone_number={self.phone_number})>"


class TimeTables(db.Model):
    __tablename__ = 'timetables'
    id = db.Column(db.Integer, db.Sequence('datetime_id_seq'), primary_key=True)
    master = db.Column(db.String)
    date = db.Column(db.Date)
    time = db.Column(db.JSON, nullable=False, server_default="{}")

    def __repr__(self):
        return f"<TimeTables(master='{self.master}', date='{self.date}', time='{self.time}')>"


class Master(db.Model):
    __tablename__ = 'masters'
    id = db.Column(db.Integer, db.Sequence('master_id_seq'), primary_key=True)
    master_name = db.Column(db.String)
    master_user_id = db.Column(db.BigInteger, unique=True)
    master_services = db.Column(db.ARRAY(db.String))

    def __repr__(self):
        return f"<Master(master_name='{self.master_name}', master_user_id='{self.master_user_id}', " \
               f"master_services='{self.master_services}')>"


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
                name=old_service.name,
                price=service_price,
                describe=service_describe,
                pic_file_id=service_pic_file_id,
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

    async def del_service(self, name):
        service = await self.get_service(name)
        if service:
            await service.delete()
            return service
        return service

    # Методы для таблицы log
    @staticmethod
    async def get_recs_by_client(name_client):
        rec = await Records.query.where(Records.name_client == name_client).gino.first()
        return rec

    @staticmethod
    async def get_rec_by_full_datetime(full_datetime, master):
        records = await Records.query.where(Records.full_datetime == full_datetime).gino.all()
        # log = await Log.query.where(Log.name_master == master).gino.first()
        if records:
            for rec in records:
                # if log.full_datetime == full_datetime:
                if rec.name_master == master:
                    return rec
        # return log

    async def del_rec(self, full_datetime, master):
        record = await self.get_rec_by_full_datetime(full_datetime, master)
        if record:
            await record.delete()
            # return log
        # return log

    @staticmethod
    async def get_old_recs(current_datetime):
        current_date = datetime.date(current_datetime.year, current_datetime.month, current_datetime.day)
        recs = []
        for rec in await Records.query.gino.all():
            if rec.date < current_date:
                recs.append(rec)
        return recs

    @staticmethod
    async def get_recs_only_date(date, master):
        records_list = await Records.query.where(Records.date == date).gino.all()
        return_recs = []
        for line in records_list:
            if line.name_master == master and line.date == date:
                return_recs.append(line)
        return return_recs

    @staticmethod
    async def is_client_full_datetime_in_db(full_datetime, name_client):
        records = await Records.query.where(Records.full_datetime == full_datetime).gino.all()
        for rec in records:
            if rec.name_client == name_client:
                return True
        return False

    async def is_this_rec_in_db(self, name_client):
        record = await self.get_rec_by_full_datetime(name_client)
        if record:
            return True
        return False

    @staticmethod
    async def is_this_rec_5_in_db(user_id):
        record = await Records.query.where(Records.user_id == user_id).gino.first()
        if record:
            num_one_user_id = 0
            for i in [rec.user_id for rec in await Records.query.gino.all()]:
                if i == record.user_id:
                    num_one_user_id += 1
                if num_one_user_id == 5:
                    return True
        return False

    @staticmethod
    async def get_all_recs_by_user_id(user_id):
        recs = await Records.query.where(Records.user_id == user_id).gino.all()
        return recs

    async def add_rec(self, user_id, name_client, name_master, service, full_datetime, date, time, phone_number):
        rec_one = await self.get_rec_by_full_datetime(full_datetime, name_master)
        # full_log_one = await self.full_get_log(user_id, name_client, name_master, service, date, time, phone_number)
        if rec_one:
            await rec_one.update(
                id=rec_one.id,
                user_id=rec_one.user_id,
                name_client=rec_one.name_client,
                name_master=rec_one.name_master,
                service=rec_one.service,
                full_datetime=rec_one.full_datetime,
                date=rec_one.date,
                time=rec_one.time,
                phone_number=rec_one.phone_number
            ).apply()
            return rec_one
        new_rec = Records()
        new_rec.user_id = user_id
        new_rec.name_client = name_client
        new_rec.name_master = name_master
        new_rec.service = service
        new_rec.full_datetime = full_datetime
        new_rec.date = date
        new_rec.time = time
        new_rec.phone_number = phone_number
        await new_rec.create()
        return new_rec

    # Мeтоды для таблицы datetime
    @staticmethod
    async def get_timetable(datetime_one, master):
        # datetime_list = await Datetime.query.where(Datetime.datetime == datetime).gino.all()
        timetable_list = await TimeTables.query.where(TimeTables.master == master).gino.all()
        for line in timetable_list:
            if line.date == datetime_one:
                return line

    @staticmethod
    async def get_old_timetables(current_datetime):
        current_date = datetime.date(current_datetime.year, current_datetime.month, current_datetime.day)
        datetime_many = []
        for date_one in await TimeTables.query.gino.all():
            if date_one.date < current_date:
                datetime_many.append(date_one)
        return datetime_many

    async def del_timetable(self, datetime_one, master):
        timetable_one = await self.get_timetable(datetime_one, master)
        if timetable_one:
            await timetable_one.delete()
            return
        return

    async def get_dict_of_time(self, datetime_one, master):
        datetime_first = await self.get_timetable(datetime_one, master)
        return datetime_first.time

    async def add_rec_timetable(self, date, master):
        timetable_first = await self.get_timetable(date, master)
        if timetable_first:
            return True
        timetable_first = TimeTables()
        timetable_first.date = date
        timetable_first.master = master
        timetable_first.time = {'10:00': False, '10:30': False, '11:00': False, '11:30': False,
                                '12:00': False, '12:30': False, '13:00': False, '13:30': False,
                                '14:00': False, '14:30': False, '15:00': False, '15:30': False,
                                '16:00': False, '16:30': False, '17:00': False}
        await timetable_first.create()
        return False

    async def add_update_date(self, date, time, master):
        timetable_first = await self.get_timetable(date, master)
        if timetable_first:
            time_str = f'{time.hour}:{str(time.minute).ljust(2, "0")}'
            dict_time = timetable_first.time
            if dict_time[time_str] is False:
                dict_time[time_str] = True
            elif dict_time[time_str] is True:
                dict_time[time_str] = False
            await timetable_first.update(
                id=timetable_first.id,
                master=timetable_first.master,
                date=timetable_first.date,
                time=dict_time
            ).apply()
            return timetable_first
        timetable_first = TimeTables()
        timetable_first.master = master
        timetable_first.date = date
        timetable_first.time = time
        await timetable_first.create()
        return timetable_first

        # Методы таблицы masters

    @staticmethod
    async def get_master(master_name):
        master = await Master.query.where(Master.master_name == master_name).gino.first()
        return master

    async def is_this_master_in_db(self, master_name):
        master = await self.get_master(master_name)
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

    async def get_master_and_id(self):
        return {master.master_name: str(master.master_user_id) for master in await self.all_masters()}

    async def del_master(self, name):
        master = await self.get_master(name)
        if master:
            await master.delete()
            return master
        return master
