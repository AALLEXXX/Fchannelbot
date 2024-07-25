from typing import Any
from core.database.db import async_session_maker
from sqlalchemy import ResultProxy, RowMapping, insert, select, update, and_


class BaseDAO:
    model = None

    @classmethod
    async def get_all_by_params(cls, **data) -> list:
        async with async_session_maker() as session:
            filters = [getattr(cls.model, key) == value for key, value in data.items()]
            query = select(cls.model).filter(and_(*filters))
            result: ResultProxy = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def find_by_id(cls, model_id: int) -> RowMapping | Any | None:
        async with async_session_maker() as session:
            query = select(cls.model.__table__.columns).filter(cls.model.id == model_id)
            result: ResultProxy = await session.execute(query)
            return result.mappings().one_or_none()

    @classmethod
    async def add(cls, **data) -> None:

        async with async_session_maker() as session:
            query = insert(cls.model.__table__).values(**data)
            await session.execute(query)
            await session.commit()

    @classmethod
    async def update_by_id(cls, model_id, **data) -> None:
        async with async_session_maker() as session:
            condition = cls.model.__table__.c.id == model_id
            query = update(cls.model.__table__).where(condition).values(**data)
            await session.execute(query)
            await session.commit()
