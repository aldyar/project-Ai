from sqlalchemy import Column, Integer, BigInteger, String, Enum, DateTime, Boolean, ForeignKey, Date
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from datetime import datetime, date


engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3', echo=True)
async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass

# Модель пользователя
class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)  # Уникальный идентификатор пользователя
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)  # Telegram ID
    subscription_id: Mapped[int] = mapped_column(Integer, ForeignKey('subscriptions.id'), nullable=False)  # Связь с подпиской
    gpt_model: Mapped[str] = mapped_column(String, default='gpt-4o-mini')
    verification_free: Mapped[bool] = mapped_column(Boolean, default=False)
    registration_date: Mapped[date] = mapped_column(Date, default=date.today)  # Дата регистрации


# Модель тарифа
class Subscription(Base):
    __tablename__ = 'subscriptions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)  # Уникальный идентификатор подписки
    plan_name: Mapped[str] = mapped_column(Enum('free', 'mini', 'start', 'premium', name='plan_names'),nullable=False,default='free')
    start_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)  # Дата начала подписки
    end_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)  # Дата окончания подписки
    gpt_4_mini_limit: Mapped[int] = mapped_column(Integer, default=5)  # Лимит GPT 4o Mini
    gpt_4_limit: Mapped[int] = mapped_column(Integer, default=0)  # Лимит GPT 4
    gpt_4_omni_limit: Mapped[int] = mapped_column(Integer, default=0)  # Лимит GPT 4o Omni
    gpt_o1_limit: Mapped[int] = mapped_column(Integer, default=0)  # Лимит GPT 4o Omni
    dalle_limit: Mapped[int] = mapped_column(Integer, default=0)  # Лимит DALL-E


class Channels(Base):
    __tablename__ = 'channels'

    id = Column(Integer, primary_key=True, autoincrement=True)  # ID канала
    channel_name = Column(String, nullable=False, unique=True)  # Название канала


# Асинхронное создание таблиц
async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)