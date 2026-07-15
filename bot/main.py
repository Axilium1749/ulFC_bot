import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.exceptions import TelegramBadRequest
from aiogram.enums import ParseMode
from dotenv import load_dotenv
from contextlib import suppress
import asyncio
from state import active_chats
from database.db import async_session, Message as MessageModel
from middlewares import DatabaseMiddleware
from context import get_smart_context
from config import BOT_TOKEN, TOOLS
from ai import call_factchekcer, call_summarizer
from anim import animate_status

load_dotenv()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


dp.update.middleware(DatabaseMiddleware())


@dp.message(F.reply_to_message, F.text.contains("@ulFC_bot"))
async def handle_factcheck_request(message: Message):
    target_message_id = message.reply_to_message.message_id
    chat_id = message.chat.id
    
    if chat_id in active_chats:
        try: 
            await bot.delete_message(chat_id, message.message_id)
        except:
            await message.reply("Can't delete")
            return
    
    active_chats.append(chat_id)

    async def cleanup():
        await asyncio.sleep(60)
        if chat_id in active_chats:
            active_chats.remove(chat_id)
    
    cleanup_task = asyncio.create_task(cleanup())

    try:
        status_msg = await message.reply("`[   ]` *Gathering context*", parse_mode=ParseMode.MARKDOWN)
        animation_task = asyncio.create_task(animate_status(status_msg, "Gathering context"))

        context, target_msg = await get_smart_context(chat_id, target_message_id)

        animation_task.cancel()
        animation_task = asyncio.create_task(animate_status(status_msg, "Summarizing context"))

        summarized_content = await call_summarizer(context, target_msg)

        animation_task.cancel()
        animation_task = asyncio.create_task(animate_status(status_msg, "Fact-checking"))

        final_response = await call_factchekcer(summarized_content, target_msg, TOOLS)

        animation_task.cancel()

        with suppress(TelegramBadRequest):
            await status_msg.edit_text(final_response)
        
        cleanup_task.cancel()

    finally:
        if chat_id in active_chats:
            active_chats.remove(chat_id)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())