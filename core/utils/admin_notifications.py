from aiogram import Bot

from core.database.requests import UserDAO


async def notify_admins(bot: Bot, text: str):
    admins = await UserDAO.get_all_by_params(role='admin')
    for admin in admins:
        await bot.send_message(admin.chat_id, text)