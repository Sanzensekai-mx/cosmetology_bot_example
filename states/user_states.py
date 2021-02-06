from aiogram.dispatcher.filters.state import StatesGroup, State


class UserAppointment(StatesGroup):
    AppointmentSetName = State()
    AppointmentSetService = State()
    AppointmentSetMaster = State()
