from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from aiogram.fsm.storage.redis import RedisStorage


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, storage: RedisStorage):
        self.storage = storage

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:

        user = f"user{event.from_user.id}"

        check_user = await self.storage.redis.get(name=user)

        if check_user:
            await self.storage.redis.incr(name=user)
            if int(check_user.decode()) >= 3:
                return await event.answer(
                    "We have detected suspicious activity. Wait 15 seconds"
                )
            return await handler(event, data)
        await self.storage.redis.set(name=user, value=1, ex=15)
        return await handler(event, data)
