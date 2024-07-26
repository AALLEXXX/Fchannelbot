from typing import Any, List

from sqlalchemy import select, ResultProxy, RowMapping, update, and_, join

from core.database.basedao import BaseDAO
from core.database.db import async_session_maker
from core.database.models import User, UsersSub

from datetime import datetime


class UserDAO(BaseDAO):
    model = User

    @classmethod
    async def find_by_chat_id(cls, id: int) -> RowMapping | Any | None:
        async with async_session_maker() as session:
            query = select(cls.model.__table__.columns).filter(cls.model.chat_id == id)
            result: ResultProxy = await session.execute(query)
            return result.mappings().one_or_none()


    @classmethod
    async def find_admin_by_id(cls, id: int ) -> RowMapping | Any | None:
        async with async_session_maker() as session:
            query = select(cls.model.__table__.columns).filter((cls.model.chat_id == id) & (cls.model.role == 'admin'))
            result: ResultProxy = await session.execute(query)
            return result.mappings().one_or_none()

    @classmethod
    async def update_by_tg_username(cls, tg_username, **data) -> None:
        async with async_session_maker() as session:
            condition = cls.model.__table__.c.tg_username == tg_username
            query = update(cls.model.__table__).where(condition).values(**data)
            await session.execute(query)
            await session.commit()

    @classmethod
    async def find_by_tg_username(cls, tg_username: str) -> RowMapping | Any | None:
        async with async_session_maker() as session:
            query = select(cls.model.__table__.columns).filter(cls.model.tg_username == tg_username)
            result: ResultProxy = await session.execute(query)
            return result.mappings().one_or_none()





class UsersSubsDAO(BaseDAO):
    model = UsersSub

    @classmethod
    async def check_user_access(cls, username: str) -> bool:
        async with async_session_maker() as session:
            now = datetime.now()
            query = select(cls.model.__table__.columns).filter(and_(cls.model.tg_username == username, cls.model.date_from <= now, cls.model.date_to >= now))
            q_result: ResultProxy = await session.execute(query)
            user_sub = q_result.mappings().one_or_none()
            if user_sub and user_sub.link == None:
                return True
            return False

    @classmethod
    async def update_link_by_username(cls, username: str, link: str) -> bool:
        async with async_session_maker() as session:
            now = datetime.now()
            query = update(cls.model).where(and_(cls.model.tg_username == username),
                                            cls.model.date_from <= now, cls.model.date_to >= now).values(link=link)
            await session.execute(query)
            await session.commit()
            return True

    @classmethod
    async def get_sub_dateto_by_chat_id(cls, chat_id: int):
        async with (async_session_maker() as session):
            now = datetime.now()
            qr = (select(UsersSub.date_to)
                  .select_from(User)
                  .join(UsersSub, User.tg_username == UsersSub.tg_username)
                  .where(and_(User.chat_id == chat_id, UsersSub.date_to <= now, UsersSub.date_to >= now))
                  )
            result = await session.execute(qr)
            return result.mappings().one_or_none()

    @classmethod
    async def check_user_access_on_join(cls, chat_id: int):
        async with (async_session_maker() as session):
            now = datetime.now()
            qr = (select(UsersSub.date_to)
                  .select_from(User)
                  .join(UsersSub, User.tg_username == UsersSub.tg_username)
                  .where(and_(User.chat_id == chat_id, UsersSub.date_from <= now, UsersSub.date_to >= now))
                  )
            q_result = await session.execute(qr)
            res = q_result.mappings().one_or_none()
            if res is None:
                return False
            return True

    @classmethod
    async def find_user_by_link(cls, link: str) -> User | None:
        async with async_session_maker() as session:
            query = (select(User)
                    .select_from(User)
                     .join(UsersSub, User.tg_username == UsersSub.tg_username)
                     .where(UsersSub.link == link)
                     )
            q_result = await session.execute(query)
            return q_result.scalars().one_or_none()


    @classmethod
    async def get_dates_from_all_users_for_kick(cls) -> List[dict]:
        async with (async_session_maker() as session):
            """"
            select date_to, users_subs.tg_username, chat_id 
            from users_subs 
            inner join users on users_subs.tg_username = users.tg_username
            """
            query = (select(UsersSub.date_to, UsersSub.tg_username, User.chat_id).select_from(UsersSub)
                     .join(User, User.tg_username == UsersSub.tg_username))
            q_result = (await session.execute(query)).mappings().all()
            print(q_result)
            return q_result

