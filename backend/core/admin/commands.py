from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from core.database.requests import UsersSubsDAO, UserDAO
from core.filters.isadmin import IsAdmin
from aiogram.fsm.state import State, StatesGroup
from config import settings

from core.handlers.channel_handler import kick_user

admin_router = Router()
class StepsAdd(StatesGroup):
    WAITING_USERNAME = State()


@admin_router.message(Command("admin"), IsAdmin())
async def start_admin(msg: Message):
    await msg.answer("Панель фуриса \n\n"
                     "/add - отправь username пользователя")


@admin_router.message(Command("add"), IsAdmin())
async def add(msg: Message, state: FSMContext):
    await state.set_state(StepsAdd.WAITING_USERNAME)
    await msg.answer("Отправь мне username пользователя")


@admin_router.message(Command("manual_remove"), IsAdmin())
async def manual_remove(msg: Message, apscheduler: AsyncIOScheduler, bot: Bot):
    data = await UsersSubsDAO.get_dates_from_all_users_for_kick()
    await bot.send_message(settings.ADMIN_ID, text=f"логи мануал удаления")
    for dict in data:
        try:
            chat_id = dict["chat_id"]
            date_to = dict["date_to"]
            username = dict["tg_username"]
            if date_to > datetime.datetime.now():
                apscheduler.add_job(kick_user, trigger='date',
                                    id=f"kick_user_{chat_id}",
                                    run_date=date_to, misfire_grace_time=None,
                                    replace_existing=True,
                                    kwargs={"chat_id": settings.channel_id, "user_id": chat_id})
                await bot.send_message(settings.ADMIN_ID, text=f"юзер {username} {chat_id} будет исключен {date_to}")
            else:
                if await bot.unban_chat_member(chat_id=settings.channel_id, user_id=chat_id):
                    await bot.send_message(chat_id=chat_id,
                                           text="Your size time per month in the telegram channel has expired, you need to resume access to it by re-purchasing")
                    await bot.send_message(settings.ADMIN_ID,
                                           text=f"юзер {username} {chat_id} исключен")
                else:
                    await bot.send_message(chat_id=settings.ADMIN_ID,
                                           text=f'Не удалось кикнуть пользователя user_chat_id {chat_id}.')
        except Exception as e:
            await bot.send_message(chat_id=settings.ADMIN_ID,
                                   text=f'ошибка в цикле \n {e}')



@admin_router.message(StepsAdd.WAITING_USERNAME, IsAdmin())
async def process_username(msg: Message, state: FSMContext, bot: Bot):
    username = msg.text.strip()
    now = datetime.datetime.now()

    try:
        if not(await UserDAO.find_by_tg_username(tg_username=username)):
            await UserDAO.add(role='user', tg_username=username)
        await UsersSubsDAO.add(date_from=now, date_to=now + datetime.timedelta(days=30), tg_username=username)
        await msg.answer(f"Вы ввели username: {username}. Принял пользователя")

    except Exception as e:
        await msg.answer("произошла ошибка. ошибка отправлена разработчику")
        await bot.send_message(chat_id=settings.ADMIN_ID, text=f"{e} - ошибка при добавлении пользователя админом")

    await state.clear()


