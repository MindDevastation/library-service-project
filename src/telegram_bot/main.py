import os
import sys

import asyncio
import logging

from aiogram import types
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "library.settings")

from aiogram import Bot, Dispatcher, Router

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from telegram_bot.activity import user_last_activity, user_sessions
from telegram_bot.services.db import disconnect_db
from config import BOT_TOKEN
from handlers import start, stop, auth, books, borrowing, me, help


logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()


dp.include_router(start.router)
dp.include_router(stop.router)
dp.include_router(auth.router)
dp.include_router(books.router)
dp.include_router(borrowing.router)
dp.include_router(me.router)
dp.include_router(help.router)


async def end_session(user_id: int, message: types.Message, state: FSMContext):
    if state:
        await state.clear()
    await disconnect_db()

    await message.answer(
        "🚫 Your session has been terminated.\n"
        "To start again, use the /start command.",
        parse_mode=ParseMode.MARKDOWN,
    )
    logging.info(f"Ending session for user {user_id}")


async def check_inactivity():
    logging.info("Starting inactivity check loop")
    while True:
        current_time = asyncio.get_event_loop().time()
        logging.info(f"Checking inactivity... Current time: {current_time}")

        logging.info(f"Current user_last_activity: {user_last_activity}")

        if not user_last_activity:
            logging.info("No users in user_last_activity, skipping inactivity check.")
        else:
            for user_id, last_activity in list(user_last_activity.items()):
                logging.info(
                    f"User {user_id} last activity: {last_activity}. "
                    f"Diff from current time: {current_time - last_activity}"
                )
                if current_time - last_activity > 300:
                    session = user_sessions.get(user_id)
                    logging.info(f"Session: {session} for User {user_id}")

                    if session:
                        message, state = session
                        await end_session(user_id, message, state)
                        del user_last_activity[user_id]
                        del user_sessions[user_id]
                        logging.info(
                            f"Session ended for user {user_id} due to inactivity."
                        )

        await asyncio.sleep(60)


async def on_start():
    logging.info("Starting bot...")
    asyncio.create_task(check_inactivity())
    logging.info("Inactivity check task created.")


async def on_shutdown():
    logging.warning("Shutting down bot...")
    await bot.close()


async def main():
    logging.info("Bot is up and running!")
    await on_start()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
