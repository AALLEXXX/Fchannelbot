from aiogram.filters import CommandStart
from aiogram.types import Message

from core.database.models import User
from core.database.requests import UserDAO, UsersSubsDAO
from datetime import datetime, timedelta
from aiogram import Router, Bot
from config import settings

user_router = Router()

@user_router.message(CommandStart())
async def first_user_start_handler(msg: Message, bot: Bot):
    chat_id = msg.chat.id
    name = msg.from_user.first_name
    tg_username = msg.from_user.username

    if tg_username == None:
        return await msg.answer("You have hidden your username. To continue working with the bot, add a username to your account")

    answer_msg = f"Hi, {name}. "

    #проверяем если админ добавил пользователя и пользователь зашел впервые то обновляем его данные в таблице, если
    # юзер сам по себе зашел то пишем ему что нужно сделать
    user: User = await UserDAO.find_by_tg_username(tg_username=tg_username)
    if user and user.reg_date is None:
        await UserDAO.update_by_tg_username(tg_username, chat_id=chat_id, name=name, reg_date=datetime.now())
    elif user is None:
        await UserDAO.add(tg_username=tg_username, chat_id=chat_id, name=name, role="user", reg_date=datetime.now())
        return await msg.answer(text='you need buy access, you can do it on payhip, when you done send the proof to furys discord')


    try:
        if await UsersSubsDAO.check_user_access(tg_username):
            link = await bot.create_chat_invite_link(settings.channel_id, member_limit=1, expire_date=timedelta(hours=3))
            res = await UsersSubsDAO.update_link_by_username(tg_username, link.invite_link)
            if res:
                answer_msg += f"Thanks for the purchase, your link -\n{link.invite_link}"

    except Exception as e:
        await msg.answer(text="Sorry, there was an error, I have already notified the developers about it. they will help you soon")
        return await bot.send_message(chat_id=settings.ADMIN_ID, text=f"ошибка - {str(e)} \n ошибка при генерации ссылки. юзернейм пользователя - {tg_username}")

    await msg.answer(answer_msg)

