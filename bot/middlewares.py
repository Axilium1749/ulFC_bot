from aiogram import BaseMiddleware
from datetime import datetime, timezone
from aiogram.types import Message
from database.db import async_session, Message as MessageModel


class DatabaseMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data: dict):

        message = None

        if isinstance(event, Message):
            message = event
        elif hasattr(event, 'message'):
            message = event.message

        print(f"DEBUG: Пришло сообщение. Текст: {message.text}, От кого: {message.from_user}")

        if message.text and message.from_user and not message.from_user.is_bot:
            async with async_session() as session:
                # Всегда сохраняем время в UTC
                new_msg = MessageModel(
                    message_id=message.message_id,
                    chat_id=message.chat.id,
                    user_name=message.from_user.username or "unknown",
                    text=message.text,
                    reply_to_id=message.reply_to_message.message_id if message.reply_to_message else None,
                    created_at=datetime.now(timezone.utc)
                )

                session.add(new_msg)
                print(f"Добавлено сообщение в дб в {datetime.now(timezone.utc)}")
                await session.commit()

        return await handler(event, data)