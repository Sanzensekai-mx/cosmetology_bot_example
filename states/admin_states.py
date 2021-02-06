from aiogram.dispatcher.filters.state import StatesGroup, State


class AdminMailing(StatesGroup):
    MailingMenu = State()
    Text = State()
    Media = State()
    AnotherMedia = State()
    Forward = State()
    AddButton = State()
