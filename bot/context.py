from datetime import timedelta, timezone
from sqlalchemy import select

from database.db import async_session, Message as MessageModel
from config import SESSION_THRESHOLD, TIME_WINDOW

# Порог затишья между сессиями (30 минут)


def get_utc_now():
    """Возвращает текущее время в UTC"""
    return timezone.utc


async def get_message_by_id(session, chat_id: int, message_id: int):
    """Вспомогательная функция для быстрого поиска сообщения по TG ID"""
    result = await session.execute(
        select(MessageModel).where(
            MessageModel.chat_id == chat_id,
            MessageModel.message_id == message_id
        )
    )
    return result.scalar_one_or_none()


async def get_session_for_message(session, chat_id: int, start_msg: MessageModel) -> list[MessageModel]:
    """
    Находит всю сессию (цепочку общения) вокруг конкретного сообщения.
    Границы определяются паузами во времени > 30 минут.
    """

    # Приводим дату к timezone-aware для корректного сравнения
    start_time = start_msg.created_at.replace(tzinfo=timezone.utc) if start_msg.created_at.tzinfo is None else start_msg.created_at

    result = await session.execute(
        select(MessageModel)
        .where(
            MessageModel.chat_id == chat_id,
            MessageModel.created_at.between(
                start_time - TIME_WINDOW,
                start_time + TIME_WINDOW
            )
        )
        .order_by(MessageModel.created_at.asc())
    )
    candidates = result.scalars().all()

    if not candidates:
        return [start_msg]

    # Находим индекс нашего стартового сообщения в выборке
    try:
        target_idx = next(i for i, m in enumerate(candidates) if m.message_id == start_msg.message_id)
    except StopIteration:
        return [start_msg]

    session_messages = [start_msg]

    # 1. Идем назад по времени от целевого сообщения
    current_time = start_time
    for i in range(target_idx - 1, -1, -1):
        msg = candidates[i]
        msg_time = msg.created_at.replace(tzinfo=timezone.utc) if msg.created_at.tzinfo is None else msg.created_at
        if current_time - msg_time <= SESSION_THRESHOLD:
            session_messages.append(msg)
            current_time = msg_time
        else:
            break

    # 2. Идем вперед по времени от целевого сообщения
    current_time = start_time
    for i in range(target_idx + 1, len(candidates)):
        msg = candidates[i]
        msg_time = msg.created_at.replace(tzinfo=timezone.utc) if msg.created_at.tzinfo is None else msg.created_at
        if msg_time - current_time <= SESSION_THRESHOLD:
            session_messages.append(msg)
            current_time = msg_time
        else:
            break

    # Возвращаем отсортированную сессию
    session_messages.sort(key=lambda x: x.created_at.replace(tzinfo=timezone.utc) if x.created_at.tzinfo is None else x.created_at)
    return session_messages


def format_output(messages: list[MessageModel]) -> str:
    return "\n".join([f"{m.user_name}: {m.text}" for m in messages])


async def get_smart_context(chat_id: int, target_message_id: int) -> tuple[str, MessageModel]:
    """
    Главная функция. Собирает текущую сессию + родительские сессии (рекурсия = 1).
    """
    async with async_session() as session:

        target_msg = await get_message_by_id(session, chat_id, target_message_id)

        if not target_msg:
            print('не найдено ЦЕЛЕВОЕ')
            return "", None

        main_session = await get_session_for_message(session, chat_id, target_msg)

        # Набор для отслеживания дубликатов по message_id
        collected_ids = {m.message_id for m in main_session}
        final_context_raw = list(main_session)

        # 3. Проверяем ответы на старые сессии (Рекурсия глубина = 1)
        for msg in main_session:
            if msg.reply_to_id and msg.reply_to_id not in collected_ids:
                parent_msg = await get_message_by_id(session, chat_id, msg.reply_to_id)
                if parent_msg:
                    parent_session = await get_session_for_message(session, chat_id, parent_msg)

                    for pm in parent_session:
                        if pm.message_id not in collected_ids:
                            final_context_raw.append(pm)
                            collected_ids.add(pm.message_id)

        final_context_raw.sort(key=lambda x: x.created_at.replace(tzinfo=timezone.utc) if x.created_at.tzinfo is None else x.created_at)

        final_context = format_output(final_context_raw)

        return final_context, target_msg