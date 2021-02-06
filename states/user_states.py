from aiogram.dispatcher.filters.state import StatesGroup, State


class UserAppointment(StatesGroup):
    Name = State()
    Service = State()
    Master = State()
