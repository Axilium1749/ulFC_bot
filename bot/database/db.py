from datetime import datetime, timezone
from sqlalchemy import BigInteger, String, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
import sys, os
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)
from config import DATABASE_URL

# Подключаемся к базе, которую мы создали в докере
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine)

class Base(DeclarativeBase):
    pass

class Chat(Base):
    __tablename__ = 'chats'
    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, unique=True)

class Message(Base):
    __tablename__ = 'messages'
    id: Mapped[int] = mapped_column(primary_key=True)
    message_id: Mapped[int] = mapped_column(BigInteger)
    chat_id: Mapped[int] = mapped_column(BigInteger)  # Просто ID для связи
    user_name: Mapped[str] = mapped_column(String(100), nullable=True)
    text: Mapped[str] = mapped_column(nullable=True)
    reply_to_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)