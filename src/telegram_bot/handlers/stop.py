import asyncio
import logging

from aiogram import types, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from telegram_bot.activity import user_last_activity, user_sessions
from telegram_bot.services.db import disconnect_db

router = Router()


@router.message(Command("stop"))
async def stop(message: types.Message, state: FSMContext):
    telegram_id = message.from_user.id
    user_last_activity[telegram_id] = asyncio.get_event_loop().time()
    user_sessions[telegram_id] = (message, None)

    logging.info(f"User {telegram_id} initiated session termination.")
    logging.info(
        f"Updated user activity: {telegram_id} -> {user_last_activity[telegram_id]}"
    )
    logging.info(f"Current user activity dictionary: {user_last_activity}")

    await state.clear()

    try:
        await disconnect_db()
    except Exception as e:
        logging.error(f"Error disconnecting from database: {e}")
        await message.answer(
            "⚠️ An error occurred while disconnecting from the database."
        )

    await message.answer(
        "🚫 Your session has been terminated.\n"
        "To start again, use the /start command.",
        parse_mode=ParseMode.MARKDOWN,
    )
