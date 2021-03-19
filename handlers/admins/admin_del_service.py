import logging
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, \
    CallbackQuery, ContentType

from keyboards.default import main_menu_admin
from keyboards.inline import cancel_add_master
from loader import dp, bot
from states.admin_states import AdminAddMaster
from utils.db_api.models import DBCommands
from data.config import admins
from handlers.users.appointment import return_kb_mes_services

db = DBCommands()