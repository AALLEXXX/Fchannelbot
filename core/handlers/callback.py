import logging

from aiogram import Bot, F
from aiogram.types import CallbackQuery
from core.handlers.first_start_handler import user_router


# call.data - get_closed_chat
@user_router.callback_query(F.data == "get_closed_chat")
async def get_closed_chat(call: CallbackQuery, bot: Bot):
    msg_id = call.message.message_id
    chat_id = call.message.chat.id
    await bot.delete_message(chat_id, msg_id)
    await call.message.answer("NNN")