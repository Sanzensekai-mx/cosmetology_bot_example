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
    Masters = State()
    Confirm = State()


class AdminDelService(StatesGroup):
    Del = State()


class AdminCheckLog(StatesGroup):
    ChoiceRange = State()
    CheckToday = State()
    CheckWeek = State()
    CheckMonths = State()


class AdminAddMaster(StatesGroup):
    Name = State()
    ID = State()
    Services = State()
    Confirm = State()


class AdminDelMaster(StatesGroup):
    Del = State()
