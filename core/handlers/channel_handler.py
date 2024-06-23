from aiogram import Router, Bot
from aiogram.filters import ChatMemberUpdatedFilter, IS_NOT_MEMBER, IS_MEMBER
from aiogram.types import ChatMemberUpdated
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import settings
from core.database.requests import UsersSubsDAO

channel_router = Router()

async def kick_user(bot: Bot, chat_id: int, user_id: int):
    try:
        if await bot.unban_chat_member(chat_id=chat_id, user_id=user_id):
            await bot.send_message(chat_id=user_id, text="Your size time per month in the telegram channel has expired, you need to resume access to it by re-purchasing")
        else:
            await bot.send_message(chat_id=settings.ADMIN_ID,
                                   text=f'Не удалось кикнуть пользователя user_chat_id {user_id}.')
    except Exception as e:
        await bot.send_message(chat_id=settings.ADMIN_ID, text=f'Произошла ошибка при кике пользователя user_chat_id - {user_id}. Ошибка {e}')



@channel_router.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def on_user_join(event: ChatMemberUpdated, apscheduler: AsyncIOScheduler, bot: Bot):
    chat_id = event.from_user.id

    if not(await UsersSubsDAO.check_user_access_on_join(chat_id=chat_id)):
        print(event.invite_link.invite_link)


        msg_text = f"Кто то пытался зайти в канал по чужой ссылке не имея доступа.\n" \
                    f"Пользователь chat_id - {chat_id} username - {event.from_user.username}. \n"


        rat = await UsersSubsDAO.find_user_by_link(link=event.invite_link.invite_link)
        if not (rat is None):
            msg_text += f"Ему передал ссылку юзер - {rat.tg_username} chat_id - {rat.chat_id}"


        await bot.send_message(chat_id=settings.ADMIN_ID,
                               text=msg_text)

        return await bot.unban_chat_member(chat_id=settings.channel_id, user_id=chat_id)

    date_to = await UsersSubsDAO.get_sub_dateto_by_chat_id(chat_id=chat_id)
    print(date_to)
    print(date_to.date_to)
    # apscheduler.add_job(kick_user, trigger='date',
    #                     run_date=dt.datetime.now() + dt.timedelta(minutes=15), misfire_grace_time=None,
    #                     kwargs={"chat_id": settings.test_channel_id, "user_id": event.from_user.id})

    apscheduler.add_job(kick_user, trigger='date',
                        run_date=date_to.date_to, misfire_grace_time=None,
                        kwargs={"chat_id": settings.channel_id, "user_id": chat_id})
