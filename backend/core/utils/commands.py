from aiogram import Bot

from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChat

from core.database.requests import UserDAO


async def set_commands(bot: Bot):
    all_user_commands = [
        BotCommand(
            command='start',
            description='get chat'
        )
    ]

    admin_commands = [
        BotCommand(
            command="admin",
            description='get admin panel'
        ),
        BotCommand(
            command="add",
            description='add user'
        )
    ]


    await bot.set_my_commands(all_user_commands, BotCommandScopeDefault())

    admins = await UserDAO.get_all_by_params(role='admin')
    for admin in admins:
        await bot.set_my_commands(admin_commands, BotCommandScopeChat(chat_id=admin.chat_id))
