import os
import subprocess
from datetime import datetime, timedelta
from aiogram import Bot
from aiogram.types import FSInputFile
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncAttrs
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from config import settings

engine = create_async_engine(settings.DATABASE_URL_POSTGRES, echo=True)

async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    pass


def backup_database(db_name, user, host, port, password, backup_file) -> bool:
    pg_dump_command = [
        "pg_dump",
        f"--dbname=postgresql://{user}:{password}@{host}:{port}/{db_name}",
        "-F", "c",  # Формат бэкапа (custom)
        "-f", backup_file
    ]

    try:
        subprocess.run(pg_dump_command, check=True)
        print(f"Backup successful: {backup_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error during backup: {e}")
        return False


async def send_backup_to_admin(admin_chat_id : int, bot: Bot):
    backup_file = os.path.join("/", f"{settings.DB_NAME}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql")

    old_backup_filename = f"{settings.DB_NAME}_backup_{(datetime.now() - timedelta(days=1)).strftime('%Y%m%d_%H%M%S')}.sql"
    backup_file_path = os.path.join("/", old_backup_filename)

    # print(old_backup_filename)
    # Delete old backup file if it exists
    try:
        if os.path.exists(backup_file_path):
            os.remove(backup_file_path)
            # print(f"Deleted old backup file: {old_backup_filename}")
    except Exception as e:
        await bot.send_message(admin_chat_id, f"Ошибка при удалении старого бекапа: {e}")

    res = backup_database(
        user=settings.DB_USER,
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        password=settings.DB_PASS,
        db_name=settings.DB_NAME,
        backup_file=backup_file
    )
    if res:
        backup = FSInputFile(backup_file)
        await bot.send_document(chat_id=admin_chat_id, document=backup, caption="База данных")
    else:
        await bot.send_message(chat_id=admin_chat_id, text=f"не удалось создать бекап."
                                                           f"\n название файла - {backup_file} \n "
                                                           f"путь - {backup_file_path}")



async def schedule_backup_db_file(apscheduler: AsyncIOScheduler, bot: Bot):
    apscheduler.add_job(send_backup_to_admin, trigger='cron',
                        hour='4', minute='0', second='0',
                        kwargs={'admin_chat_id': int(settings.ADMIN_ID), }
                        )
    await bot.send_message(int(settings.ADMIN_ID), f"Создана задача бекапа. Бекап будет отправлен в 4 часа утра ")