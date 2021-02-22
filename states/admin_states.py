from aiogram.dispatcher.filters.state import StatesGroup, State


class AdminMailing(StatesGroup):
    MailingMenu = State()
    Text = State()
    Media = State()
    AnotherMedia = State()
    Forward = State()
    AddButton = State()


class AdminAddService(StatesGroup):
    Name = State()
    Price = State()
    Describe = State()
    PicHref = State()
    Time = State()
    Confirm = State()


class AdminCheckLog(StatesGroup):
    ChoiceRange = State()
    CheckToday = State()
    CheckWeek = State()
    CheckMonths = State()
