import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import settings
from core.admin.commands import admin_router
from core.database.db import schedule_backup_db_file
from core.handlers.channel_handler import channel_router

from core.handlers.first_start_handler import user_router
from core.middlewares.apschedulerMiddleware import SchedulerMiddleware

from core.middlewares.throttlingMiddleware import ThrottlingMiddleware
from apscheduler_di import ContextSchedulerDecorator

from core.utils.admin_notifications import notify_admins
from core.utils.commands import set_commands


async def stop(bot: Bot):
    await notify_admins(bot=bot, text="Этот бро прекратил свою работу")

async def start() -> None:


    bot = Bot(token=settings.bots.bot_token)
    storage = RedisStorage.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0"
    )
    dp = Dispatcher(storage=storage)
    # dp.shutdown.register(stop)


    dp.message.middleware.register((ThrottlingMiddleware(storage=storage)))
    jobstores = {
        "default": RedisJobStore(
            jobs_key="dispatcher_trips_jobs",
            run_times_key="dispatched_trips_running",
            host=settings.REDIS_HOST,
            db=2,
            port=settings.REDIS_PORT,
        )
    }

    job_defaults = {
        'coalesce': True,
        'max_instances': 3
    }

    await set_commands(bot)

    scheduler = ContextSchedulerDecorator(
        AsyncIOScheduler(timezone="Europe/Moscow", jobstores=jobstores)
    )
    scheduler.ctx.add_instance(bot, declared_class=Bot)
    scheduler.start()

    dp.update.middleware.register(SchedulerMiddleware(scheduler))

    dp.include_router(user_router)
    dp.include_router(admin_router)
    dp.include_router(channel_router)

    try:
        #await schedule_backup_db_file(scheduler, bot)
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"[!!! Exceprion - {e}]", exc_info=True)
        await notify_admins(bot=bot, text=f"Бот упал с ошибкой\n{e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(start())
