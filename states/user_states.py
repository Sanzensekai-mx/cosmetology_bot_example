from aiogram.dispatcher.filters.state import StatesGroup, State


class UserAppointment(StatesGroup):
    Name = State()
    Master = State()
    Service = State()
    Date = State()
    Time = State()
    PhoneNumber = State()
    Confirm = State()


class UserCheckLog(StatesGroup):
    Check = State()
