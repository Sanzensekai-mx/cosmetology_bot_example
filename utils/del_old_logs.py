import datetime
import asyncio
import aioschedule
from utils.db_api.models import DBCommands
from data.config import admins
from loader import bot

db = DBCommands()


async def del_logs_and_datetime():
    # current_date = datetime.datetime.now(tz_ulyanovsk)
    current_date = datetime.datetime.now()
    current_date += datetime.timedelta(hours=4)
    old_logs = await db.get_old_recs(current_date)
    old_datetime = await db.get_old_timetables(current_date)
    for log in old_logs:
        await db.del_rec(log.full_datetime, log.name_master)
    for d in old_datetime:
        await db.del_timetable(d.datetime, d.master)
    for admin in admins:
        await bot.send_message(chat_id=admin, text='Старые записи удалены из базы данных.')


async def del_old_logs():
    aioschedule.every().day.at("00:00").do(del_logs_and_datetime)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)
