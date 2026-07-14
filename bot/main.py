import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from dotenv import load_dotenv

from database.db import async_session, Message as MessageModel
from middlewares import DatabaseMiddleware
from context import get_smart_context
from config import BOT_TOKEN, TOOLS
from ai import call_factchekcer, call_summarizer

load_dotenv()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


dp.update.middleware(DatabaseMiddleware())


@dp.message(F.reply_to_message, F.text.contains("@ulFC_bot"))
async def handle_factcheck_request(message: Message):
    target_message_id = message.reply_to_message.message_id
    chat_id = message.chat.id
    context, target_msg = await get_smart_context(chat_id, target_message_id)

    summarized_content = await call_summarizer(context, target_msg)

    final_response = await call_factchekcer(summarized_content, target_msg, TOOLS)

    await message.reply(f"{final_response}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())