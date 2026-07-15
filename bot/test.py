import asyncio
from unittest.mock import MagicMock

from aiogram.types import Message as AiogramMessage
from sqlalchemy import delete

from database.db import async_session, Message as MessageModel
from middlewares import DatabaseMiddleware
from context import get_smart_context
from config import TOOLS
from ai import call_summarizer, call_factchekcer


async def _noop_handler(event, data):
    """Заглушка-обработчик вместо настоящего aiogram-хендлера.

    Должна быть async: DatabaseMiddleware в конце делает `await handler(...)`.
    """
    return None


async def run_test():
    # 1. Очистка БД перед тестом
    async with async_session() as session:
        await session.execute(delete(MessageModel))
        await session.commit()
    print("--- База данных очищена ---")

    # 2. Наполнение БД тестовыми сообщениями через Middleware
    db_middleware = DatabaseMiddleware()
    chat_id = 123456

    # (username, text, message_id, reply_to_message_id)
    messages_data = [
        ("Алексей", "Финляндия запретит наличку в 2027.",          1001, None),
        ("Марина", "Это миф, такого закона нет.",                  1002, 1001),
        ("Алексей", "В ЦБ подтвердили запрет с января 2027.",      1003, 1001),
    ]

    for username, text, message_id, reply_to_id in messages_data:
        # Подменяем __class__, чтобы в DatabaseMiddleware сработал
        # `isinstance(event, Message)` и middleware работал именно с этим
        # объектом, а не с левым `event.message` (обычный MagicMock отвечает
        # True на любой hasattr и уходит во вторую ветку middleware).
        # spec=Message не подходит: у pydantic-модели aiogram поля не видны
        # через dir()/hasattr(), и mock запретит доступ к .chat и т.п.
        fake_msg = MagicMock()
        fake_msg.__class__ = AiogramMessage
        fake_msg.text = text
        fake_msg.chat.id = chat_id
        fake_msg.from_user.username = username
        fake_msg.from_user.is_bot = False
        fake_msg.message_id = message_id
        if reply_to_id is not None:
            fake_msg.reply_to_message = MagicMock()
            fake_msg.reply_to_message.message_id = reply_to_id
        else:
            fake_msg.reply_to_message = None

        # Прогоняем сообщение через middleware — оно само запишет его в БД
        await db_middleware(_noop_handler, fake_msg, {})

    print("--- Тестовые сообщения добавлены в БД ---")

    # 3. Запуск основного цикла проверки (как в main.py -> handle_factcheck_request)
    # Фактчеким самое первое утверждение Алексея
    target_message_id = 1001

    print("--- Запуск пайплайна фактчекинга ---")

    context, target_msg = await get_smart_context(chat_id, target_message_id)

    summarized_content = await call_summarizer(context, target_msg)
    print(f"Саммари: {summarized_content}")

    final_response = await call_factchekcer(summarized_content, target_msg, TOOLS)

    print(f"\n--- Итоговый ответ бота ---\n{final_response}")


if __name__ == "__main__":
    asyncio.run(run_test())
