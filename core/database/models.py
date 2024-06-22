from core.database.db import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, ForeignKey


class User(Base):
    __tablename__ = "users"
    chat_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=True)
    role: Mapped[str] = mapped_column(nullable=True)
    reg_date: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    tg_username: Mapped[str] = mapped_column(nullable=False, unique=True)

    users_subs = relationship("UsersSub", back_populates="user")


class UsersSub(Base):
    __tablename__ = "users_subs"
    id : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    date_from : Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    date_to : Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    link: Mapped[str] = mapped_column(unique=True, nullable=True)
    tg_username : Mapped[str] = mapped_column(ForeignKey("users.tg_username"), nullable=False, unique=True)

    user = relationship("User", back_populates="users_subs")
