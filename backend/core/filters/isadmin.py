from typing import List, Tuple
from aiogram.filters import Filter
from aiogram.types import Message

from core.database.requests import UserDAO


class IsAdmin(Filter):
    async def __call__(self, msg: Message) -> bool:
        chat_id: int = msg.from_user.id
        admins: List[Tuple[str,]] = await UserDAO.get_all_by_params(role='admin')
        if any(admin.chat_id == chat_id for admin in admins):
            return True
        return False
