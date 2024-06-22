from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
import datetime
from core.database.requests import UsersSubsDAO, UserDAO
from core.filters.isadmin import IsAdmin
from aiogram.fsm.state import State, StatesGroup
from config import settings
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


